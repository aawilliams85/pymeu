import configparser
import olefile
import os

from . import decompress
from . import types

INFORMATION_NAME = '_INFORMATION'

def _create_upgrade_dat(version: types.MEFupVersion, card: types.MEFupCard) -> str:
    # There is an upgrade.dat file which needs to be created
    # from the content in the upgrade.inf file.
    fields = [
        f'PLAT={version.plat}',
        f'OS={version.os}',
        f'ME={version.me}',
        f'KEP={version.kep}',
        f'MINOS={version.minos}',
        f'MAXOS={version.maxos}',
        f'ARD={version.ard}',
        f'RAM={card.ram_size_bytes}',
        f'ISC={card.storage_size_bytes}',
        f'FP={card.fp_size}'
    ]
    result = ';'.join(fields) + ';\r\n'
    return result

def _get_upgrade_dat(streams: list[types.MEArchive]) -> types.MEArchive:
    inf = next(x for x in streams if x.name == 'upgrade.inf')
    manifest = _deserialize_me_fup_manifest(inf.data.decode('utf-8'))
    dat_file = _create_upgrade_dat(manifest.version, manifest.otw)
    data = bytearray(dat_file, 'utf-16-le')
    return types.MEArchive(
        name='Upgrade.dat',
        data=data,
        path=['Upgrade.dat'],
        size=len(data)
    )

def _deserialize_me_fup_manifest(ini_content: str) -> types.MEFupManifest:
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(ini_content)

    # Version Header
    version_section = config['version']
    version = types.MEFupVersion(
        plat=int(version_section['Platform']),
        os=version_section['OS'],
        me=version_section['ME'],
        kep=version_section['KEP'],
        minos=version_section['MINOS'],
        maxos=version_section['MAXOS'],
        ard=int(version_section['ARD'])
    )
    
    # Firmware Card
    fwc_section = config['FWC']
    fwc = types.MEFupCard(
        files=[],
        ram_size_bytes=int(fwc_section.get('AddRamSize', 0)),
        storage_size_bytes=int(fwc_section.get('AddISCSize', 0)),
        fp_size=int(fwc_section.get('AddFPSize', 0))
    )

    # Over-The-Wire
    otw_section = config['OTW']
    otw = types.MEFupCard(
        files=[],
        ram_size_bytes=int(otw_section.get('AddRamSize', 0)),
        storage_size_bytes=int(otw_section.get('AddISCSize', 0)),
        fp_size=int(otw_section.get('AddFPSize', 0))
    )

    # Drivers
    try:
        drivers_list = [(key, int(value)) for key, value in config.items('KEPDRIVERS')]
    except:
        drivers_list = []
    drivers = types.MEFupDrivers(
        drivers=drivers_list
    )

    return types.MEFupManifest(
        version=version,
        fwc=fwc,
        otw=otw,
        drivers=drivers
    )

def fup_to_disk(fup_path: str, output_path: str):
    # Application-specific handling for *.FUP files
    #
    # This results in an intermediate form that can be used to
    # form the firmware upgrade card or over-the-wire format.

    # Create output folder if it doesn't exist yet
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)

    with olefile.OleFileIO(fup_path) as ole:
        streams = decompress.decompress_archive(ole, output_path)

        # In the *.FUP packages specifically, there is some data
        # in the upgrade.inf file that needs to be arranged into
        # an Upgrade.dat file.
        streams.append(_get_upgrade_dat(streams))
        for stream in streams:
            # In *.FUP packages specifically, there are some _INFORMATION files
            # that don't need to be exported
            if stream.name.endswith(INFORMATION_NAME): continue

            stream_output_path = decompress._create_subfolders(output_path, stream.path)
            with open(stream_output_path, 'wb') as f:
                f.write(stream.data)