# pymetransfer

Pymetransfer (Python ME Transfer) is a set of helper functions built around pycomm3 to interface with Rockwell Automation PanelView Plus 6/7 HMIs.<br>

The current release is very limited in scope, and has only been tested on a very limited selection of hardware.  It is alpha quality at best and could easily brick your device.  Use at your own risk.<br>

## Example

Use the download function to transfer a *.MER file to the remote terminal:

```python
from pymetransfer.main import *
met = METransfer('192.168.1.20')
met.download('C:\\YourFolder\\YourProgram.mer')
```

Use the reboot function to restart the remote terminal:

```python
from pymetransfer.main import *
met = METransfer('192.168.1.20')
met.reboot()
```