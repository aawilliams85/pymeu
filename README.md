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