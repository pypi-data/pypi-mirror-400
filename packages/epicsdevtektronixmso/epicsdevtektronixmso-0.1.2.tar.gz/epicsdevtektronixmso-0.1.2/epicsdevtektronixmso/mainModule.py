"""Server of Tektronix MSO oscilloscopes for EPICS PVAccess.
"""
# pylint: disable=invalid-name
__version__= 'v0.1.2 2026-01-06'# error handling improved, cleanup
#TODO: remove WFMOutpre? query from acquire_waveforms.

import sys
#import os
import time
from time import perf_counter as timer
from collections import namedtuple
import threading
import re
import numpy as np

import pyvisa as visa

from p4p.nt import NTScalar, NTEnum
from p4p.nt.enum import ntenum
from p4p.server import Server
from p4p.server.thread import SharedPV

class C_():
    """Namespace for module properties"""
    AppName = 'epicsDevTektronixMSO'
    verbose = 0
    pargs = None# Program arguments from main()
    cycle = 0
    lastRareUpdate = 0.
    server = None
    serverState = ''

    # Applications-specific constants
    scope = None
    PvDefs = []
    PVs = {}# dictionary of {pvName:PV}
    scpi = {}# {pvName:SCPI} map
    setterMap = {}
    readSettingQuery = None
    timeDelta = {}# execution times of different operations
    tstart = 0.
    exceptionCount = {}
    numacq = 0
    triggersLost = 0
    trigTime = 0
    channelsTriggered = ''
    prevTscale = 0.

#Conversion map of python variables to EPICS types
EpicsType = {
    bool:   '?',
    str:    's',
    int:    'i',
    float:  'd',
    bytes:  'Y',
    type(None): 'V',
}
#``````````````````Constants``````````````````````````````````````````````````
Threadlock = threading.Lock()
PORT = ':4000'# IP port of the instrument
OK = 0
IF_CHANGED =True
ElapsedTime = {}
BigEndian = False# Defined in configure_scope(WFMOUTPRE:BYT_Or LSB)
#```````````````````Helper methods````````````````````````````````````````````
def printTime(): return time.strftime("%m%d:%H%M%S")
def printi(msg): print(f'inf_@{printTime()}: {msg}')
def printw(msg):
    txt = f'WAR_@{printTime()}: {msg}'
    print(txt)
    publish('status',txt)
def printe(msg):
    txt = f'ERR_{printTime()}: {msg}'
    print(txt)
    publish('status',txt)
def _printv(msg, level):
    if C_.verbose >= level: print(f'DBG{level}: {msg}')
def printv(msg): _printv(msg, 1)
def printvv(msg): _printv(msg, 2)
def printv3(msg): _printv(msg, 3)

def pvobj(pvname):
    """Return PV named as pvname"""
    pvsEntry = C_.PVs[pvname]
    return next(iter(pvsEntry.values()))

def pvv(pvname):
    """Return PV value"""
    return pvobj(pvname).current()

def publish(pvname, value, ifChanged=False, t=None):
    """Post PV with new value"""
    try:
        pv = pvobj(pvname)
    except KeyError:
        return
    if t is None:
        t = time.time()
    if not ifChanged or pv.current() != value:
        pv.post(value, timestamp=t)

def query(pvnames, explicitSCPIs=None):
    """Execute query request of the instrument for multiple PVs"""
    scpis = [C_.scpi[pvname] for pvname in pvnames]
    if explicitSCPIs:
        scpis += explicitSCPIs
    combinedScpi = '?;:'.join(scpis) + '?'
    r = C_.scope.query(combinedScpi)
    return r.split(';')

def configure_scope():
    """Configure the data formatting parameters of the scope"""
    print('>configure_scope')
    C_.scope.write('HORizontal:DELay:MODe ON')
    C_.scope.write('HORizontal:MODE MANual')
    C_.scope.write('HORizontal:MODE:MANual:CONFIGure HORIZontalscale')

    #C_.scope.write('DATa:ENCdg SRIBINARY')
    C_.scope.write((  ':WFMOUTPRE:ENCdg BINARY;'
                        ':WFMOUTPRE:BN_Fmt RI;'
                        ':WFMOUTPRE:BYT_NR 2;'
                        f':WFMOUTPRE:BYT_Or LSB;'))

#``````````````````Initialization and run``````````````````````````````````````
def start():
    """Start p4p server and run it until C_.serverState = Exited"""
    init()
    set_server('Start')

    # Loop
    C_.server = Server(providers=list(C_.PVs.values()))
    printi(f'Start server with polling interval {pvv("polling")}')
    while not C_.serverState.startswith('Exit'):
        time.sleep(pvv("polling"))
        if not C_.serverState.startswith('Stop'):
            poll()
    printi('Server is exited')

def init():
    """Module initialization"""
    init_visa()
    create_PVs()
    adopt_local_setting()

def poll():
    """Poll the instrument and process data"""
    C_.cycle += 1
    tnow = time.time()
    if tnow - C_.lastRareUpdate > 1.:
        C_.lastRareUpdate = tnow
        rareUpdate()

    if trigger_is_detected():
        acquire_waveforms()

    #print(f'poll {C_.cycle}')

def rareUpdate():
    """Called for infrequent updates"""
    printvv(f'rareUpdate {time.time()}')
    with Threadlock:
        r = query(['actOnEvent'],['DATE?;:TIMe'])
    publish('actOnEvent', r[0], IF_CHANGED)
    publish('dateTime', ' '.join(r[1:3]).replace('"',''))
    publish('scopeAcqCount', C_.numacq, IF_CHANGED)
    publish('lostTrigs', C_.triggersLost, IF_CHANGED)
    #print(f'ElapsedTime: {ElapsedTime}')
    publish('timing', [(round(-i,6)) for i in ElapsedTime.values()])
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#``````````````````Initialization functions```````````````````````````````````
def create_PVs():
    """Create PVs from PvDefs"""
    #``````````````````Definition of PVs``````````````````````````````````````
    R,W = False,True # values for the 'writable' field 
    # abbreviations of EPICS Value fields
    U,CL,CH = 'display.units','control.limitLow','control.limitHigh'
    # abbreviations of extra fields
    LV,SCPI,SET = 'legalValues', 'SCPI', 'setter'
    PvDef = namedtuple('PvDef',
[   'name',     'desc',                             'value', 'writable', 'fields', 'extra'], defaults=[False,{},{}])
    C_.PvDefs = [

# Mandatory PVs
PvDef('version',    'Program version',              __version__),
PvDef('status',     'Server status',                ''),
PvDef('server',     'Server control',               'Stop', W, {},
    {LV:'Start,Stop,Clear,Exit,Started,Stopped,Exited',SET:set_server}),
PvDef('polling',    'Polling interval',              1.0, W, {U:'S'}),

# instruments's PVs
PvDef('hostPort',   'IP_address:port',              C_.pargs.addr+PORT, R),
PvDef('instrCtrl',  'Scope control commands',       '*OPC', W, {},
    {LV:'*OPC,*OPC?,*CLS?,*RST,!d,*TST,*IDN?,ACQuire:STATE?,AUTOset EXECute'}),
PvDef('instrCmdS',  'Execute a scope command',      '*IDN?', W, {},
    {SET:set_instrCmdS}),
PvDef('instrCmdR',  'Response of the instrCmdS',    ''),
PvDef('timing',     'Timing: [trigger,waveforms,publish_wf,query_wf,preamble]', [0.], R, {U:'S'}),

# scope-specific PVs
PvDef('dateTime',   'Scope`s date & time',          '?'),#, R, {},{SCPI:'DATE?;:TIMe'}),
PvDef('acqCount',   'Number of acquisition recorded', 0),
PvDef('scopeAcqCount',  'Acquisition count of the scope', 0, R, {},
    {SCPI:'ACQuire:NUMACq'}),
PvDef('recLength',  'Number of points per waveform', 1000, W, {},
    {CL: 100, CH:1000000, SCPI:'HORizontal:RECOrdlength'}),
PvDef('samplingRate', 'Sampling Rate',              0., W, {U:'Hz'},
    {SCPI:'HORizontal:SAMPLERate'}),
PvDef('timePerDiv', 'Horizontal scale',             2.e-6, R, {U:'S'},
    {SCPI: 'HORizontal:SCAle'}),
PvDef('tAxis',      'Array of horizontal axis',     [0.], R, {U:'S'}),
PvDef('date',       'Scope date time',              '?'),
PvDef('lostTrigs',  'Number of triggers lost',      0),
PvDef('trigger',    'Click to force trigger event to occur', 'Trigger',W,{},
    {LV:'Force!,Trigger', SET:set_trigger}),
PvDef('trigSource', 'Trigger source',               'CH1', W, {},
    {LV:'CH1,CH2,CH3,CH4,CH5,CH6,CH7,CH8,LINE,AUX', SCPI:'TRIGger:A:EDGE:SOUrce'}),
PvDef('trigLevel',   'Trigger level',               0., W, {U:'V'},
    {SET:set_trigLevel}),
PvDef('trigDelay',   'Trigger delay',               0., W, {U:'S'},
    {SCPI:'HORizontal:DELay:MODe ON;:HORizontal:DELay:TIMe'}),
PvDef('trigHoldoff', 'Time after trigger when it will not accept another triggers',
    5.0E-3, W, {U:'S'}, {SCPI:'TRIGger:A:HOLDoff:TIMe'}),
PvDef('trigSlope',  'Trigger slope',                'RISE', W, {},
    {LV:'RISE,FALL,EITHER', SCPI:'TRIGger:A:EDGE:SLOpe'}),
PvDef('trigCoupling',   'Trigger coupling',         'DC', W, {},
    {LV:'DC,HFRej,LFRej,NoiseRej', SCPI:'TRIGger:A:EDGE:COUPling'}),
PvDef('trigMode',   'Trigger mode. Should be NORMAL.', 'NORMAL', W, {},
    {LV:'NORMAL,AUTO', SCPI:'TRIGger:A:MODe'}),
PvDef('trigState',  'State of the triggering system, Should be: READY', '?', R, {},
    {SCPI:'TRIGger:STATE'}),
PvDef('actOnEvent', 'Enables the saving waveforms on trigger', 0, W, {},
    {CL: 0, CH:1, SCPI:'ACTONEVent:ENable'}),
PvDef('aOE_Limit',  'Limit of Action On Event saves',   80, W, {},
    {SCPI:'ACTONEVent:LIMITCount'}),
PvDef('setup', 'Save/recall instrument state',      'Setup', W, {},
    {SET:set_setup, LV:'Save,Recall,Setup'}),
    ]
    # Templates for channel-related PVs
    ChannelTemplates = [
PvDef('c$VoltsPerDiv', 'Vertical sensitivity',      0., W, {U:'V/du'},
    {SCPI:'CH$:SCAle'}),
PvDef('c$Position',    'Vertical position',         0., W, {U:'du'},
    {SCPI:'CH$:OFFSet 0;POSition'}),
PvDef('c$Coupling',    'Coupling',                  'DC', W, {},
    {LV:'AC,DC', SCPI:'CH$:COUPling'}),
PvDef('c$Termination', 'Termination',               '50.000', W, {U:'Ohm'},
    {LV:'50.000,1.0000E+6', SCPI:'CH$:TER'}),
PvDef('c$OnOff',   'Trace On/Off',                  '0', W, {},
    {LV:'0,1', SCPI:'DISplay:WAVEView1:CH$:STATE'}),
PvDef('c$Waveform', 'Channel data',                  [0.], R),
PvDef('c$Peak2Peak',   'Peak to peak amplitude',    0., R, {U:'du'}),
    ]
    # extend PvDefs with channel-related PVs
    for pvdef in ChannelTemplates:
        for ch in range(C_.pargs.channels):
            newname = pvdef.name.replace('$',str(ch+1))
            fields = pvdef
            newpvdef = PvDef(newname, *fields[1:])
            C_.PvDefs.append(newpvdef)

    # Create PVs from updated PvDefs
    for pvdef in C_.PvDefs:
        count = 1
        if isinstance(pvdef.value, str):
            first = pvdef.value
        else:
            try:
                first = pvdef.value[0]
                count = len(pvdef.value)
                if count == 1:
                    count = 0# variable array
            except TypeError:
                first = pvdef.value
                count = 1
        ptype = EpicsType[type(first)]
        if count != 1:
            ptype = 'a'+ptype 
        printvv(f'>creating {pvdef.name} of type {ptype}, v:{pvdef.value}')
        ts = time.time()

        # handle the field 'extra'
        if len(pvdef.extra) == 0:
            normativeType = NTScalar(ptype, display=True, control=pvdef.writable)
            value = pvdef.value
        else:
            # handle legalValues
            lv = pvdef.extra.get(LV)
            if lv is None:
                normativeType = NTScalar(ptype, display=True, control=pvdef.writable)
                value = pvdef.value
            else:
                lv = lv.split(',')
                try:
                    idx = lv.index(pvdef.value)
                except ValueError:
                    printe(f'Could not create PV for {pvdef.name}: its value {pvdef.value} is not in legalValues')
                    sys.exit(1)
                normativeType = NTEnum(control=pvdef.writable)
                value = {'choices': lv, 'index': idx}
                printvv(f'LegalValues of {pvdef.name}: {lv}, value: {value}')

        # create PV
        try:
            pv = SharedPV(nt=normativeType)
            pv.open(value)
            if isinstance(normativeType,NTEnum):
                pv.post(value, timestamp=ts)
            else:
                V = pv._wrap(value, timestamp=ts)
                V['display.description'] = pvdef.desc
                for k,v in pvdef.fields.items():
                    V[k] = v
                pv.post(V)
        except Exception as e:
            printw(f'Could not create PV for {pvdef.name}: {str(e)[:200]}')
            continue
        pv.name = C_.pargs.prefix + pvdef.name

        # for writables we need to add setters
        if pvdef.writable:
            @pv.put
            def handle(pv, op):
                ct = time.time()
                v = op.value()
                vr = v.raw.value
                printvv(f'v type: {type(v)} = {v}, {vr}')
                if isinstance(v, ntenum):
                    vr = v
                corename = pv.name.removeprefix(C_.pargs.prefix)

                printv(f'setting {corename} to {vr}')
                # execute SCPI command for corresponding PVs
                scpi = C_.scpi.get(corename)
                setter = C_.setterMap.get(corename)
                if setter: # it is higher priority
                    printv(f'>setter[{setter}]')
                    setter(vr)
                    # value could change by the setter
                    if corename not in ['instrCmdS']:
                        printv(f'update vr of {corename}: {vr}')
                        vr = pvv(corename)
                elif scpi:
                    printv(f'>scopeCmd({scpi})')
                    scopeCmd(f'{scpi} {vr}')

                pv.post(vr, timestamp=ct) # update subscribers
                op.done()

        if C_.pargs.listPVs:
            printi(f'PV {pv.name} created: {pv}')
        C_.PVs[pvdef.name] = {pv.name:pv}

    # Make a map of pvNames to SCPI commands and a combined query for all SCPI-related parameters
    printv('>make_par2scpiMap and setterMap')
    for pvdef in C_.PvDefs:
        scpi = pvdef.extra.get('SCPI')
        if scpi:
            scpi = scpi.replace('$',pvdef.name[1])
            # remove lower case letter for brevity
            scpi = ''.join([char for char in scpi if not char.islower()])
            # check, if scpi is correct:
            if C_.verbose > 1:
                s = scpi+'?'
                printvv(f'>query {s}')
                C_.scope.query(s)
            if not scpi[0] in '!*':
                C_.scpi[pvdef.name] = scpi
        setter = pvdef.extra.get('setter')
        if setter:
            C_.setterMap[pvdef.name] = setter
    # add special case of TrigLevel
    C_.scpi['trigLevel'] = trigLevelCmd()

    C_.readSettingQuery = '?;:'.join(C_.scpi.values()) + '?'
    printv(f'setterMap: {C_.setterMap}')
    printv(f'readSettingQuery:\n{C_.readSettingQuery}')

def init_visa():
    '''Init VISA interface to device'''
    try:
        C_.rm = visa.ResourceManager('@py')
    except ModuleNotFoundError as e:
        printe(f'in visa.ResourceManager: {e}')
        sys.exit(1)

    rn = C_.pargs.addr+PORT.replace(':','::')
    resourceName = 'TCPIP::'+rn+'::SOCKET'
    printi(f'Open resource {resourceName}')
    C_.scope = C_.rm.open_resource(resourceName)
    C_.scope.set_visa_attribute( visa.constants.VI_ATTR_TERMCHAR_EN, True)
    C_.scope.timeout = 2000 # ms
    print('C_scope created')
    try:
        C_.scope.write('*CLS') # clear ESR, previous error messages will be cleared
    except Exception as e:
        printe(f'Resource {resourceName} not responding: {e}')
        sys.exit()
    C_.scope.write('*OPC')# that does not work!
    resetNeeded = False
    try:    printi('*OPC?'+C_.scope.query('*OPC?'))
    except: 
        printw('*OPC? failed'); resetNeeded = True
    try:    printi('*ESR?'+C_.scope.query('*ESR?'))
    except: 
        printw('*ESR? failed'); resetNeeded = True

    if resetNeeded:
        printw('To recover the scope a command !d was sent')
        C_.scope.write('!d') 
        sys.exit(1)

    idn = C_.scope.query('*IDN?')
    print(f"IDN: {idn}")
    if not idn.startswith('TEKTRONIX'):
        print('ERROR: instrument is not TEKTRONIX')
        sys.exit(1)

    C_.scope.encoding = 'latin_1'
    C_.scope.read_termination = '\n'#Important.

    configure_scope()

# def close_visa(C_):
    # C_.rm.close()
    # C_.scope = None

#``````````````````Setters
def set_instrCmdS(cmd):
    """Setter for the instrCmdS PV"""
    return scopeCmd(cmd, True)

def set_server(state=None):
    """setter for the server PV"""
    #printv(f'>set_server({state}), {type(state)}')
    if state is None:
        state = pvv('server')
        printi(f'Setting server state to {state}')
    state = str(state)
    if state == 'Start':
        printi('starting the server')
        configure_scope()
        adopt_local_setting()
        publish('server','Started')
    elif state == 'Stop':
        printi('server stopped')
        publish('server','Stopped')
    elif state == 'Exit':
        printi('server is exiting')
        publish('server','Exited')
    elif state == 'Clear':
        publish('acqCount', 0)
        #publish('lostTrigs', 0)
        C_.triggersLost = 0
        publish('status','Cleared')
        # set server to previous state
        set_server(C_.serverState)
    C_.serverState = state
    return OK

def set_setup(action):
    """setter for the setup PV"""
    action = str(action)
    with Threadlock:
        if action == 'Save':
            C_.scope.write("SAVE:SETUP 'c:/latest.set'")
        elif action == 'Recall':
            if str(pvv('server')).startswith('Start'):
                printw('Please set server to Stop before Recalling')
                publish('setup','Setup')
                return
            C_.scope.write("RECAll:SETUp 'c:/latest.set'")
        elif action != 'Setup':
            printw(f'WAR: wrong setup action: {action}')
    if action == 'Recall':
        adopt_local_setting()
    publish('setup','Setup')

def set_trigger(action):
    action = str(action)
    if action.startswith('Force'):
        C_.scope.write('TRIGger FORCe')
    publish('trigger','Trigger')

def set_trigLevel(value):
    printv(f'set_trigLevel: {type(value),value}')
    with Threadlock:
        C_.scope.write(trigLevelCmd() + f' {value}')
        v = C_.scope.query(trigLevelCmd() + '?')
    publish('trigLevel',v)

#``````````````````````````````````````````````````````````````````````````````
def scopeCmd(cmd, updateCmdM=False):
    """send command to scope, update instrCmdR if needed, return 0 if OK"""
    printv(f'>scopeCmd: {cmd, updateCmdM} @{round(time.time(),6)}')
    rc = 0
    try:
        with Threadlock:
            if '?' in cmd:
                reply = C_.scope.query(cmd)
                printv(f'scope reply:{reply}')
                if updateCmdM:
                    printv('updating instrCmdR')
                    publish('instrCmdR',reply)
            else:
                C_.scope.write(cmd)
    except:
        return handle_exception('in scopeCmd(%s)'%cmd)
    printv(f'<scopeCmd {rc}')
    return rc

def handle_exception(where):
    """Handle exception"""
    #print('handle_exception',sys.exc_info())
    exceptionText = str(sys.exc_info()[1])
    tokens = exceptionText.split()
    msg = 'ERR:'+tokens[0] if tokens[0] == 'VI_ERROR_TMO' else exceptionText
    msg = msg+': '+where
    printe(msg)
    with Threadlock:
        C_.scope.write('*CLS')
    return -1

def adopt_local_setting():
    """Read scope setting and update PVs"""
    printv(f'>adopt_local_setting')
    ct = time.time()
    try:
        with Threadlock:
            values = C_.scope.query(C_.readSettingQuery).split(';')
        nothingChanged = True
        printvv(f'parnames: {C_.scpi.keys()}')
        printvv(f'C_.readSettingQuery: {C_.readSettingQuery}')
        printvv(f'values: {values}')
        if len(C_.scpi) != len(values):
            l = min(len(C_.scpi),len(values))
            printe(f'ReadSetting failed for {list(C_.scpi.keys())[l]}')
            sys.exit(1)
        for parname,v in zip(C_.scpi, values):
            pv = pvobj(parname)
            pvValue = pv.current()

            if isinstance(pvValue, ntenum):
                pvValue = str(pvValue)
            else:
                v = type(pvValue.raw.value)(v)
            printv(f'parname,v: {parname, type(v), v, type(pvValue), pvValue}')
            valueChanged = pvValue != v
            if valueChanged:
                printv(f'posting {pv.name}={v}')
                pv.post(v, timestamp=ct)
                nothingChanged = False
                printv(f'PV {pv.name} changed using local value {v}')

    except Exception as e:
        printe('Exception in adopt_local_setting:'+str(e))
    if nothingChanged:
        printi('Local setting did not change.')

def trigLevelCmd():
    """Generate SCPI command for trigger level control"""
    ch = str(pvv('trigSource'))
    if ch[:2] != 'CH':
        return ''
    r = 'TRIGger:A:LEVel:'+ch
    printv(f'tlcmd: {r}')
    return r
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#``````````````````Acquisition-related functions``````````````````````````````
def trigger_is_detected():
    """check if scope was triggered"""
    ts = timer()
    try:
        with Threadlock:
            r = query(['trigState','scopeAcqCount','recLength',
                       'timePerDiv'], ['DATa:SOUrce:AVAILable'])
    except Exception as e:
        printe(f'in query for trigger: {e}')
        for exc in C_.exceptionCount:
            if exc in str(e):
                C_.exceptionCount[exc] += 1
                errCountLimit = 2
                if C_.exceptionCount[exc] >= errCountLimit:
                    printe(f'Processing stopped due to {exc} happened {errCountLimit} times')
                    set_server('Exit')
                else:
                    printw(f'Exception  #{C_.exceptionCount[exc]} during processing: {exc}')
        return False

    # last query was successfull, clear error counts
    for i in C_.exceptionCount:
        C_.exceptionCount[i] = 0
    try:
        trigstate,numacq,rl,timePerDiv,C_.channelsTriggered = r
    except Exception as e:
        printw(f'wrong trig info: {r}, exception:{e}')
        return False
    numacq = int(numacq)
    if numacq == 0 or C_.numacq == 0:
        C_.triggersLost = 0
    else:
        C_.triggersLost += numacq - C_.numacq - 1
    C_.triggersLost = max(C_.triggersLost, 0)
    if numacq <= C_.numacq:
        C_.numacq = numacq
        return False

    C_.numacq = numacq
    C_.trigtime = time.time()
    d = {'recLength': int(rl), 'timePerDiv': float(timePerDiv),
         'trigState':trigstate}
    for pvname,value in d.items():
        publish(pvname, value, IF_CHANGED, t=C_.trigtime)
    ElapsedTime['trigger_detection'] = timer() - ts
    return True

def acquire_waveforms():
    """acquire scope waveforms"""
    printv('>acquire_waveform')
    if not C_.pargs.waveforms:
        return
    publish('acqCount', pvv('acqCount') + 1, t=C_.trigTime)
    ElapsedTime['acquire_wf'] = timer()
    ElapsedTime['publish_wf'] = 0.
    ElapsedTime['query_wf'] = 0.
    ElapsedTime['preamble'] = 0.
    channels = C_.channelsTriggered.split(',')
    if channels[0] == 'NONE':
        channels = []
    for ch in channels:
        # refresh scalings
        #TODO: this section is quite time consuming and can be avoided
        # but if we monitor XINCR, YMULT, YZERO, V/DIV separately then it takes twice longer
        ts = timer()            
        try:
            # most of the time is spent here, 4 times longer than the reading of waveform:
            with Threadlock:
                #preamble = C_.scope.query(f'DATA:SOUrce {ch};:WFMOutpre?')
                C_.scope.write(f'DATA:SOUrce {ch}')
                #dt1 = timer() - ts
                # doing WFMOutpre? outside of the acquire_waveforms saves 0.3 s
                preamble = C_.scope.query(f':WFMOutpre?')
        except Exception as e:
            printe(f'Exception in getting waveform preamble for {ch}:{e}')
            break
        dt = timer() - ts
        #print(f'dt {ch}: {dt1,dt}')
        ElapsedTime['preamble'] -= dt
        #TODO: if preamble did not change, then we can skip its decoding, we can save ~65us
        preambleMap = decode_preamble(preamble)# timing=60us
        if preambleMap is None:
            break

        xincr = float(preambleMap['XINCR'])
        ymult = float(preambleMap['YMULT'])
        yzero = float(preambleMap['YZERO'])
        vPerDiv = preambleMap['V/DIV']
        # for debugging, if query(f':WFMOutpre?') is commented out
        #xincr = 3.20E-9
        #ymult = 15.6250E-6
        #yzero = 0.
        #vPerDiv = pvv(f'c{ch[2]}VoltsPerDiv')

        if xincr != C_.prevTscale:
            msg = f'Horizontal scale changed, new tAxis. {xincr,C_.prevTscale}'
            printi(msg)
            publish('status',msg)
            C_.prevTscale = xincr
            tAxis = np.arange(pvv('recLength'))*C_.prevTscale
            publish('tAxis', list(tAxis), t=C_.trigTime)
        ts = timer()
        try:
            with Threadlock:
                bin_wave = C_.scope.query_binary_values('curve?',
                    datatype='h', is_big_endian=BigEndian,
                    container=np.array)
        except Exception as e:
            printe(f'in query_binary_values: {e}')
            break
        ElapsedTime['query_wf'] -= timer() - ts
        #printv(f'bin_wave: {bin_wave}')
        wfmax = float(bin_wave.max())
        wfmin = float(bin_wave.min())
        v = bin_wave*ymult + yzero
        v = v/vPerDiv

        ts = timer()
        publish(f'c{ch[2]}Waveform', v, t=C_.trigTime)
        #publish(f'c{ch[2]}VoltsPerDiv', vPerDiv, t=C_.trigtime)
        try:
            publish(f'c{ch[2]}Peak2Peak',
                (wfmax - wfmin)*ymult,
                t = C_.trigtime)
        except Exception as e:
            printe(f'Exception updating Peak2Peak {e}')
            #print(f'{wfmax,wfmin,preambleMap}')
        ElapsedTime['publish_wf'] -= timer() - ts
    ElapsedTime['acquire_wf'] -= timer()

#````````````````````````````Decoding of the waveform preamble````````````````
#typical preamble:
#2;16;BINARY;RI;INTEGER;LSB;"Ch1, DC coupling, 500.0mV/div, 1.000us/div, 1250 points, Sample mode";1250;Y;LINEAR;"s";8.0E-9;4.7950E-9;505;"V";78.1250E-6;0.0E+0;1.9400;TIME;ANALOG
#The element names of the wafeform preamble reported by WFMOutpre command
PreambleKeys = (
'BYT_NR; BIT_NR; ENCdg; BN_Fmt; integer; BYT_Or; WFID; NR_PT;'
'PT_FMT; PT_ORDER; XUNIT; XINCR; XZERO; PT_OFF; YUNIT; YMULT; YOFF; YZERO')
#Note, the integer field is not documented
PreambleKeys = PreambleKeys.replace(' ','').split(';')
def decode_preamble(preamble):
    """Decode the waveform preamble"""
    tokens = preamble.replace('"','').split(';')
    try:
        preambleMap = {key:v for key,v in zip(PreambleKeys,tokens)}
        wfid = preambleMap['WFID']
        voltsPerDivTxt = wfid.split(',')[2].lstrip()
        _,number,vPerDiv = re.split(r'(-?\d*\.?\d+)',
            voltsPerDivTxt)
        try:
            g = {'m':0.001, 'u':0.000001}[vPerDiv[0]]
        except:
            g = 1.
        voltsPerDiv = float(number)*g
        preambleMap['V/DIV'] = voltsPerDiv
        printvv(f'preambleMap: {preambleMap}')
    except Exception as e:
        printw(f'wrong preamble: {preamble}: {e}')
        return None
    return preambleMap
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
