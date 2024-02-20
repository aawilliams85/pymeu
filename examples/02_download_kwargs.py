from pymeu import MEUtility

'''
optional keyword arguments

ignore_terminal_valid:  Proceed regardless of whether the terminal
                        identity can be confirmed as a valid target.

overwrite:              If a file exists on the terminal with the same
                        name, overwrite it.

run_at_startup:         Set this as the default application to run.
replace_comms:          Replace terminal communications with settings
                        from file.
delete_logs:            Delete terminal logs

'''
meu = MEUtility('YourPanelViewIpAddress')
meu.download('C:\\YourFolder\\YourProgram.mer', overwrite=True)