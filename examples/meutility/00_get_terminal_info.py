"""
If filing bug reports, please include this terminal info report.
Output should be generated similar to below:

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

from pymeu import MEUtility
meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.get_terminal_info(print_log=True, redact_log=True, silent_mode=False)