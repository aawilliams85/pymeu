from pymeu import MEUtility

'''
optional keyword arguments

ignore_terminal_valid:  Proceed regardless of whether the terminal
                        identity can be confirmed as a valid target.

overwrite:              If a file exists on the local machine with the same
                        name, overwrite it.

remote_file_name:       Used to specify a different file name on the
                        remote terminal than the local machine.
'''
meu = MEUtility('YourPanelViewIpAddress')
meu.upload('C:\\YourFolder\\YourProgram.mer', overwrite=True)