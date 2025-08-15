from collections.abc import Callable
import configparser
import olefile
import os
import time
from typing import Optional
from warnings import warn

from .. import comms
from . import decompress
from . import fuwhelper
from . import helper
from . import transfer
from . import types
from . import util

INFORMATION_NAME = '_INFORMATION'
OTW_USE_WIN_DIR = [
    'locOSup.exe',
    'ebcbootrom.bin',
    'system.bin',
    'upgradeoptions.exe',
    'valOSpart.exe',
    'GetFreeRAM.exe',
    'PVPlus_Mozart_nkc.MCE',
    'EBCMOZ.EBC'
]

CE_BLACKLIST_FILES = [
    'atlce400.dll',
    'symbol.ttf',
    'times.ttf',
    'wingding.ttf'
]

def _create_upgrade_dat(
    version: types.MEFupUpgradeInfVersion,
    card: types.MEFupUpgradeInfCard, 
    me_files: types.MEFupMEFileListInf,
    ce: list[tuple[str, str]] = None
) -> str:
    # Always use windows-style
    crlf = '\r\n'

    # There is an upgrade.dat file which needs to be created
    # from the content in the upgrade.inf file.
    #
    # TODO: Take Kepware drive selection into account for final size,
    #       once useroptions are being generated
    isc_size_bytes = card.storage_size_bytes + me_files.info.size_on_disk_bytes
    fields = [
        f'PLAT={version.plat}',
        f'OS={version.os}',
        f'ME={version.me}',
        f'KEP={version.kep}',
        f'MINOS={version.minos}',
        f'MAXOS={version.maxos}',
        f'ARD={version.ard}',
        f'RAM={card.ram_size_bytes}',
        f'ISC={isc_size_bytes}',
        f'FP={card.fp_size}'
    ]
    result = ';'.join(fields) + ';' + crlf

    # If CE components are present
    if ce:
        cefiles = f'{crlf}[PVPCE]{crlf}'
        for (infile, outfile) in ce: cefiles += f'{infile}={outfile}{crlf}'
        cefiles += ('\x00')
        result += cefiles

    return result

def _get_stream_by_name(streams: list[types.MEArchive], name: str, case_insensitive=True) -> types.MEArchive:
    if case_insensitive:
        return next(x for x in streams if x.name.lower() == name.lower())
    else:
        return next(x for x in streams if x.name == name)

def _get_upgrade_inf(streams: list[types.MEArchive]) -> types.MEFupUpgradeInf:
    return _deserialize_fup_upgrade_inf(_get_stream_by_name(streams, 'upgrade.inf').data.decode('utf-8'))

def _get_mefilelist_inf(streams: list[types.MEArchive]) -> types.MEFupMEFileListInf:
    try:
        return _deserialize_fup_mefilelist_inf(_get_stream_by_name(streams, 'MEFileList.inf').data.decode('utf-8'))
    except Exception as e:
        # v6+ don't use this at all so just enter default values
        return types.MEFupMEFileListInf(info=types.MEFupMEFileListInfInfo(me='', size_on_disk_bytes=0), mefiles=[])

def _get_upgrade_dat(streams: list[types.MEArchive]) -> types.MEArchive:
    upgrade_inf_data = _get_upgrade_inf(streams)
    mefilelist_inf_data = _get_mefilelist_inf(streams)

    # Should really be the specified mode (FWC or OTW) because they can be different values.
    dat_file = _create_upgrade_dat(
        version=upgrade_inf_data.version,
        card = upgrade_inf_data.otw,
        me_files=mefilelist_inf_data,
        ce=upgrade_inf_data.ce
    )
    
    #data = bytearray(dat_file, encoding='utf-16-le')
    data = dat_file.encode('utf-16-le', errors='ignore')
    return types.MEArchive(
        name='Upgrade.dat',
        data=data,
        path=['Upgrade.dat'],
        size=len(data)
    )

def _deserialize_fup_mefilelist_inf(input: str) -> types.MEFupMEFileListInf:
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read_string(input)

    info_section = config['info']
    info = types.MEFupMEFileListInfInfo(
        me=info_section.get('ME'),
        size_on_disk_bytes=info_section.getint('SizeOnDisk', 0)
    )

    me_files_section = config['MEFILES']
    me_files = []
    for key, value in me_files_section.items():
        me_files.append(key)
    
    # Return ConfigData instance
    return types.MEFupMEFileListInf(info=info, mefiles=me_files)

def _deserialize_fup_upgrade_inf(input: str) -> types.MEFupUpgradeInf:
    config = configparser.ConfigParser(allow_no_value=True, strict=False)
    config.optionxform = str
    config.read_string(input)

    # Version Header
    version_section = config['version']
    version = types.MEFupUpgradeInfVersion(
        plat=version_section.getint('Platform', 0),
        os=version_section.get('OS'),
        me=version_section.get('ME'),
        kep=version_section.get('KEP'),
        minos=version_section.get('MINOS'),
        maxos=version_section.get('MAXOS'),
        ard=version_section.getint('ARD', 0)
    )
    
    # Firmware Card
    fwc_section = config['FWC']
    fwc_files = [
        (key, value) for key, value in fwc_section.items()
        if key not in ['AddRAMSize', 'AddISCSize', 'AddFPSize']
    ]
    fwc = types.MEFupUpgradeInfCard(
        files=fwc_files,
        ram_size_bytes=fwc_section.getint('AddRAMSize', 0),
        storage_size_bytes=fwc_section.getint('AddISCSize', 0),
        fp_size=fwc_section.getint('AddFPSize', 0)
    )

    # Over-The-Wire
    otw_section = config['OTW']
    otw_files = [
        (key, value) for key, value in otw_section.items()
        if key not in ['AddRAMSize', 'AddISCSize', 'AddFPSize']
    ]
    otw = types.MEFupUpgradeInfCard(
        files=otw_files,
        ram_size_bytes=otw_section.getint('AddRAMSize', 0),
        storage_size_bytes=otw_section.getint('AddISCSize', 0),
        fp_size=otw_section.getint('AddFPSize', 0)
    )

    # Drivers
    try:
        drivers_section = config['KEPDRIVERS']
        drivers = [(key, int(value)) for key, value in drivers_section.items()]
    except:
        drivers = []

    # CE Components
    #
    # This is where the CE files will be listed out.
    #
    # Currently does not work because there are duplicates that configparser
    # doesn't like.
    try:
        ce_section = config['PVPCE']
        ce = [(key, value) for key, value in ce_section.items()]
    except:
        ce = []

    return types.MEFupUpgradeInf(
        version=version,
        fwc=fwc,
        otw=otw,
        drivers=drivers,
        ce=ce
    )

def _path_to_list(path: str) -> list[str]:
    path = path.replace('\\', '/').lower()
    components = [comp for comp in path.split('/') if comp]
    return components if components else [path]

def fup_to_fuc(
    input_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    # Application-specific handling for *.FUP files that
    # keeps streams in memory.
    #
    # This results in an intermediate form that can be used to
    # form the firmware upgrade card or over-the-wire format.
    with olefile.OleFileIO(input_path) as ole:
        streams = decompress.decompress_archive(
            ole=ole,
            progress=progress
        )

        # In the *.FUP packages specifically, there is some data
        # in the upgrade.inf file that needs to be arranged into
        # an Upgrade.dat file.
        streams.append(_get_upgrade_dat(streams))
        return streams

def fup_to_fuc_folder(
    input_path: str,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None,
):
    # Application-specific handling for *.FUP files that
    # writes streams to a folder.
    #
    # This results in an intermediate form that can be used to
    # form the firmware upgrade card or over-the-wire format.

    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = fup_to_fuc(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        # In *.FUP packages specifically, there are some _INFORMATION files
        # that don't need to be exported
        if stream.name.endswith(INFORMATION_NAME): continue

        stream_output_path = decompress._create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)

def fup_to_fwc(
    input_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None,
) -> list[types.MEArchive]:
    # Application-specific handling for *.FUP files that
    # keeps streams in memory.
    #
    # This results in the Firmware Card format (FWC) that
    # can be used to flash a terminal via removable media.
    streams = fup_to_fuc(
        input_path=input_path,
        progress=progress
    )
    upgrade_inf = _get_upgrade_inf(streams)
    
    streams_fwc = []
    for (file, outfile) in upgrade_inf.fwc.files:
        stream = _get_stream_by_name(streams, file)
        stream.path = _path_to_list(outfile)
        streams_fwc.append(stream)

    for (file, outfile) in upgrade_inf.ce:
        dirname, basename = util.split_file_path(outfile)
        stream = _get_stream_by_name(streams, file)
        stream.path = ['upgrade', 'AddIns', basename]
        streams_fwc.append(stream)

    return streams_fwc

def fup_to_fwc_folder(
    input_path: str,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None,
):
    # Application-specific handling for *.FUP files that
    # writes streams to a folder.
    #
    # This results in the Firmware Card format (FWC) that
    # can be used to flash a terminal via removable media.

    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = fup_to_fwc(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        stream_output_path = decompress._create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)

def fup_to_otw(
    input_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    # Application-specific handling for *.FUP files that
    # keeps streams in memory.
    #
    # This results in the Over-The-Wire format (OTW) that
    # can be sent via a network connection.
    streams = fup_to_fuc(
        input_path=input_path,
        progress=progress
    )
    upgrade_inf = _get_upgrade_inf(streams)

    streams_otw = []
    for (file, outfile) in upgrade_inf.otw.files:
        stream = _get_stream_by_name(streams, file)
        stream.path = _path_to_list(outfile)
        streams_otw.append(stream)

    for (file, outfile) in upgrade_inf.ce:
        stream = _get_stream_by_name(streams, file)
        stream.path = _path_to_list(outfile)
        streams_otw.append(stream)

    return streams_otw

def fup_to_otw_folder(
    input_path: str,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None,
):
    # Application-specific handling for *.FUP files that
    # writes streams to a folder.
    #
    # This results in the Over-The-Wire format (OTW) that
    # can be sent via a network connection.  Note that OTW
    # is not usually stored in a folder so this is intended
    # just for debug.

    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = fup_to_otw(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        stream_output_path = decompress._create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)

def flash_fup_to_terminal(
    cip: comms.Driver, 
    device: types.MEDeviceInfo,
    fup_path_local: str,
    fuwhelper_path_local: str,
    fuwcover_path_local: str = None,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    # Read FUP into memory
    streams_otw = fup_to_otw(
        input_path=fup_path_local,
        progress=progress
    )

    # Determine if firmware upgrade helper already exists in one
    # of the expected locations and use it, or else transfer the
    # helper file specified.
    if helper.get_file_exists(cip, device.me_paths, '\\Windows\\FUWhelper.dll'):
        device.me_paths.fuwhelper_file = '\\Windows\\FUWhelper.dll'
    elif helper.get_file_exists(cip, device.me_paths, device.me_paths.fuwhelper_file):
        pass
    else:
        transfer.download_file(
            cip=cip,
            device=device,
            file_path_local=fuwhelper_path_local,
            file_path_terminal=device.me_paths.fuwhelper_file,
            overwrite=True,
            progress=progress
        )
        util.wait(time_sec=5, progress=progress)

    # Check major rev.  v5 process is a bit different than v6/v7A
    major_rev = int(device.me_identity.me_version.split(".")[0])

    if major_rev <= 5:
        mefilelist_inf_data = _get_mefilelist_inf(streams_otw)

        fuwhelper.set_screensaver(cip, device.me_paths, False)
        fuwhelper.set_me_corrupt_screen(cip, device.me_paths, False)
        os_rev = fuwhelper.get_os_rev(cip, device.me_paths)
        part_size = fuwhelper.get_partition_size(cip, device.me_paths)
        restore = fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\_restore_reserve.cmd')
        fuwhelper.start_process(cip, device.me_paths, 'GenReserve:0')

        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage_Card')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\upgrade')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\upgrade')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\upgrade')

        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Windows')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Windows')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Windows\\upgrade')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Windows\\upgrade')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Windows\\upgrade')

        if (fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\Step2.dat')):
            try:
                fuwhelper.delete_file(cip, device.me_paths, '\\Storage Card\\Step2.dat')
            except Exception as e:
                print(e)

        storage_free_space = fuwhelper.get_free_space(cip, device.me_paths, '\\Storage Card')
        storage_total_space = fuwhelper.get_total_space(cip, device.me_paths, '\\Storage Card')
        windows_free_space = fuwhelper.get_free_space(cip, device.me_paths, '\\Windows')
        windows_total_space = fuwhelper.get_total_space(cip, device.me_paths, '\\Windows')

        # Check files from MEFileInfo.inf?
        for file in mefilelist_inf_data.mefiles:
            fuwhelper.get_file_exists(cip, device.me_paths, f'\\Storage Card{file}')

        transfer.download_file(
            cip=cip,
            device=device,
            file_path_local=fuwcover_path_local,
            file_path_terminal='\\Windows\\FUWCover.exe',
            overwrite=True,
            progress=progress
        )
        fuwhelper.start_process(cip, device.me_paths, '\\Windows\\FUWCover.exe')
        fuwhelper.stop_process(cip, device.me_paths, 'MERuntime.exe')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\Rockwell Software\\RSViewME')

        # Delete files from MEFileInfo.inf?
        for file in mefilelist_inf_data.mefiles:
            if fuwhelper.get_file_exists(cip, device.me_paths, f'\\Storage Card{file}'):
                try:
                    fuwhelper.delete_file(cip, device.me_paths, f'\\Storage Card{file}')
                except Exception as e:
                    print(e)

        # Delete KEPServer
        if fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise'):
            fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise')
            fuwhelper.delete_folder(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise')

        for stream in streams_otw:
            # Certain CE files fail to download, still investigating
            if stream.name.lower() in CE_BLACKLIST_FILES: continue

            if stream.path[0].lower() != 'windows' and stream.path[0].lower() != 'storage card':
                # The normal files look to all have relative directories.
                #
                # Some go to \\Storage Card, others to \\Windows.
                # There is no hint in upgrade.inf file for this.
                #
                # Current guesses...
                # [1] Always redirect files after Autoapp.bat and before RFOn.bat?
                # [2] Some way to parse contents of autoapp.bat to see which are referenced?
                # [3] All binary/executable files except for known ones that belong to Storage Card?
                # [4] There is no logic to it.
                if stream.path[-1].lower() in [f.lower() for f in OTW_USE_WIN_DIR]:
                    stream_path_terminal = '\\Windows\\' + '\\'.join(stream.path)
                else:
                    stream_path_terminal = '\\Storage Card\\' + '\\'.join(stream.path)
            else:
                # The CE addon files look to all have absolute directories
                stream_path_terminal = '\\' + '\\'.join(stream.path)

            try:
                # Currently blocking this around TRY/EXCEPT just to see what happens on terminal.
                # Remove prior to release.
                warn('Still ignoring download failure for CE test!')
                transfer.download(
                    cip=cip,
                    device=device,
                    file_data=stream.data,
                    file_path_terminal=stream_path_terminal,
                    overwrite=True,
                    progress=progress
                )
            except Exception as e:
                print(e)

        # Initiate install
        fuwhelper.set_screensaver(cip, device.me_paths, True)
        fuwhelper.set_me_corrupt_screen(cip, device.me_paths, True)
        util.wait(time_sec=5, progress=progress)
        fuwhelper.stop_process(cip, device.me_paths, 'FUWCover.exe')
        fuwhelper.start_process(cip, device.me_paths, '\\Storage Card\\upgrade\\autorun.exe')
    if major_rev > 5:
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\vfs')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\vfs')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\vfs\\platform firmware')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\vfs\\platform firmware')
        if (fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\Step2.dat')):
            fuwhelper.delete_file(cip, device.me_paths, '\\Storage Card\\Step2.dat')
        if fuwhelper.get_process_running(cip, device.me_paths, 'MERuntime.exe'):
            fuwhelper.stop_process_me(cip, device.me_paths)
        fuwhelper.get_file_exists(cip, device.me_paths, '\\Windows\\useroptions.txt')

        for stream in streams_otw:
            stream_path_terminal = '\\Storage Card\\' + '\\'.join(stream.path)
            transfer.download(
                cip=cip,
                device=device,
                file_data=stream.data,
                file_path_terminal=stream_path_terminal,
                overwrite=True,
                progress=progress
            )

    return True