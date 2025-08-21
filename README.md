# pymeu

PyMEU (Python ME Utility) is a Python tool to interface with Rockwell Automation 2711P PanelView Plus terminals.  Use at your own risk.<br>

See dmroeder's [pymeu_gui](https://github.com/dmroeder/pymeu_gui) for a standalone desktop application.<br>

## Capabilities

The public classes in pymeu provide the following capabilities:

> ### MEUtility
>
> MEUtility provides the following standard functions for ME terminals (i.e. PanelView Plus products):
> - Get Terminal Info (report info on terminal identity, version, files, etc)
> - Download (transfer *.MER file from local device to terminal)
> - Upload (transfer *.MER file from terminal to local device)
> - Upload All (transfer all *.MER files from terminal to local device)
> - Reboot
>
> It also offers extended functions for native ME terminals (i.e. no PanelView Plus 7 Series B):
> - Create Firmware Card (transfer *.FUP within local device to specified path) (experimental)
> - Flash Firmware (transfer *.FUP from local device to terminal) (experimental)
> - Stop (close ME station) (experimental)

> ### CFUtility
>
> CFUtility provides the following standard functions for PanelView Plus 7 Series B terminals only:
> - Flash Firmware (transfer *.DMK from local device to terminal) (experimental)

Other internal classes and functions in pymeu may provide interesting capabilities, but are subject to more change over time.

## Getting Started

### Installation

To install from pip, run one of the following commands to install pymeu only, pymeu with pylogix as the communications driver, or pymeu with pycomm3 as the communications driver.  At least one communications driver is required.
```console
pip install pymeu
pip install pymeu[pylogix]
pip install pymeu[pycomm3]
```

To upgrade to the latest release:
```console
pip install pymeu --upgrade
```

### Examples

A good low-risk example to start with is generating a terminal info report: 
```python
from pymeu import MEUtility
meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.get_terminal_info(print_log=True)
```
See the Examples section for more code samples.

## Bug Reports

If filing bug reports, please include a copy of the terminal info report show in the example above.

## Contributing

Contributions welcome!<br>
Ideas, code, hardware testing, bug reports, etc<br>

## Acknowledgements

**[dmroeder](https://github.com/dmroeder)** for pylogix, inspiring the creation of this tool, python guidance, and various direct contributions for better functionality and compatibility. <br>
**[ottowayi](https://github.com/ottowayi)** for pycomm3 and various CIP reference materials.