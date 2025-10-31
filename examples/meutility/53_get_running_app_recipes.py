import os
import pprint

from pymeu import MEUtility
from pymeu import comms
from pymeu import me

'''
NOTE - Typically only the main MEUtility functions are intended
to be exposed for use.  Other functions (in this case from comms and
me) can allow for other interesting code to be written, but are more
likely to have breaking changes over time.

This example finds the Startup *.MER file on the remote terminal,
uploads it in memory, and extracts the RecipePlus data.
'''

meu = MEUtility(comms_path='YourTerminalIpAddress')
info = meu.get_terminal_info()
with comms.Driver(comms_path=meu.comms_path) as cip:
    device = me.validation.get_terminal_info(cip)
    mer = me.transfer.upload(
        cip=cip,
        device=device,
        file_path_terminal=f'{device.me_paths.runtime}\\{info.device.startup_mer_file}',
        progress=None
    )
    result = me.application.recipeplus_deserialize(
        input_path=bytes(mer),
        progress=None
    )
    pprint.pprint(result)