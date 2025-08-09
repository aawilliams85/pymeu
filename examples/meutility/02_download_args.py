from pymeu import MEUtility
meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.download(
    file_path_local='C:\\YourFolder\\YourProgram.mer',
    file_name_terminal='YourProgramOtherName.mer',
    delete_logs=False,
    overwrite=False,
    replace_comms=False,
    run_at_startup=True
)