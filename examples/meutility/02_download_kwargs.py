from pymeu import MEUtility
meu = MEUtility('YourPanelViewIpAddress')
meu.download('C:\\YourFolder\\YourProgram.mer', overwrite=True, remote_file_name='YourProgramOtherName.mer')