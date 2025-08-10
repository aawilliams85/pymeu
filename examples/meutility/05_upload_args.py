from pymeu import MEUtility
meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.upload(
    file_path_local='C:\\YourFolder\\YourProgram.mer', 
    file_name_terminal='YourProgramOtherName.mer',
    overwrite=True
)