# pymeu

PyMEU (Python ME Utility) is a set of helper functions built around pycomm3 to interface with Rockwell Automation PanelView Plus HMIs.<br>

Use at your own risk.<br>

## Installation

To install from pip:
```console
pip install pymeu
```

To upgrade from pip:
```console
pip install pymeu --upgrade
```

## Basic Examples

Use the download function to transfer a *.MER file to the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.download('C:\\YourFolder\\YourProgram.mer')
```

Use the upload function to transfer a *.MER file from the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.upload('C:\\YourFolder\\YourProgram.mer')
```

Use the upload all function to transfer all *.MER files from the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.upload_all('C:\\YourFolder')
```

Use the reboot function to restart the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.reboot()
```

## Bug Reports

If filing bug reports, please include this terminal info report.
Output should be generated similar to below:

```python
from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.get_terminal_info(print_log=True, redact_log=True)

"""
Terminal product type: 24.
Terminal product code: 51.
Terminal product name: PanelView Plus_6 1500.
Terminal helper version: 11.00.00.
Terminal ME version: 11.00.25.230.
Terminal major version: 11.
Terminal minor version: 1.
Terminal has 75040768 free bytes.
Terminal has MED files: ['Redacted'].
Terminal has MER files: ['Redacted', 'Redacted', 'Redacted'].
Terminal startup file: Redacted.
"""

```

## Acknowledgements

**dmroeder** for pylogix, inspiring the creation of this tool, python guidance, and various direct contributions for better functionality and compatibility.<br>
**ottowayi** for pycomm3 and various CIP reference materials.
