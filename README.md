# pymeu

PyMEU (Python ME Utility) is a set of helper functions built around pycomm3 to interface with Rockwell Automation PanelView Plus 6/7 HMIs.<br>

The current release has only been tested on a very limited selection of hardware.  It is alpha quality at best and could easily brick your device.  Use at your own risk.<br>

## Example

Use the download function to transfer a *.MER file to the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('192.168.1.20')
meu.download('C:\\YourFolder\\YourProgram.mer')
```

Use the upload function to transfer a *.MER file from the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('192.168.1.20')
meu.upload('C:\\YourFolder\\YourProgram.mer')
```

Use the upload all function to transfer all *.MER files from the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('192.168.1.20')
meu.upload_all('C:\\YourFolder')
```

Use the reboot function to restart the remote terminal:

```python
from pymeu import MEUtility
meu = MEUtility('192.168.1.20')
meu.reboot()
```