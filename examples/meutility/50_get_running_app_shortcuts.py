import os
from pymeu import MEUtility
from pymeu import me

'''
NOTE - Typically only the main MEUtility functions are intended
to be exposed for use.  The inner functions (in this case from
me.application) can allow for other interesting code to be written,
but are more likely to have breaking changes over time.

This example finds the Startup *.MER file on the remote terminal,
uploads it to the local device, and extracts the shortcut data.

me.application.get_mer_shortcuts() returns the relevant elements
from RSLinxNG.xml, but an abbreviated form is printed like below:

Shortcut SHORTCUT_1_NAME Topology:
├── <device name="FactoryTalk Linx" />
│   ├── <port name="Ethernet" portNumber="5" />
│   │   ├── <bus name="DRIVER_1_NAME" NATPrivateAddress="" />
│   │   │   ├── <port name="Port" address="192.168.1.10" portNumber="2" />
│   │   │   │   └── <device name="PLC_1_NAME" NATPrivateAddress="" />
Shortcut SHORTCUT_2_NAME Topology:
├── <device name="FactoryTalk Linx" />
│   ├── <port name="Ethernet 2" portNumber="2" />
│   │   ├── <bus name="DRIVER_2_NAME" NATPrivateAddress="" />
│   │   │   ├── <port name="A" address="192.168.1.11" portNumber="2" />
│   │   │   │   ├── <device name="PLC_2_ENT" NATPrivateAddress="" />
│   │   │   │   │   ├── <port name="Backplane" address="1" portNumber="1" />
│   │   │   │   │   │   ├── <bus name="1756-A17/A or B" NATPrivateAddress="" />
│   │   │   │   │   │   │   ├── <port name="Backplane" address="0" portNumber="1" />
│   │   │   │   │   │   │   │   └── <device name="PLC_2_NAME" NATPrivateAddress="" />
'''

meu = MEUtility(comms_path='YourTerminalIPAddress')
info = meu.get_terminal_info()
running = os.path.join('YourTempFolder', info.device.startup_mer_file)
mer = meu.upload(
    file_path_local=running,
    file_name_terminal=None,
    overwrite=True,
    progress=None
)
me.application.get_mer_shortcuts(
    input_path=running,
    print_summary=True,
    progress=None
)