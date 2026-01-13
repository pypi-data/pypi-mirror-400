# epicsDevTektronixMSO
Python-based EPICS PVAccess server for Tektronix MSO scopes.<br>

## installation and run
```
pip install  epicsDevTektronixMSO
python -m epicsDevTektronixMSO -h

```

## Test Control GUI and Plotting
Requirements:<br>
- **pypeto** python module for control application
- **pvplot** python module for plotting application

They both could be installed using ```pip install pypeto, pvplot```

To run the control application, copy /config/scopeTektronixMSO_pp.py to a folder
of your choise.
```
python -m pypeto -c folder -f scopeTektronixMSO
python -m pvplot -a V:tekMSO: "c1Waveform c2Waveform c3Waveform c4Waveform c5Waveform c6Waveform"
```
[Example of control GUI](docs/scope_pypet.png)
[Example of plotting app](docs/scope_pvplot.png)
