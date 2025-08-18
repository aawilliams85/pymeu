from collections.abc import Callable
import olefile
import os
import shutil
from typing import Optional
import xml.etree.ElementTree as ET

from . import decompress
from . import types
from . import util

MER_FTLINX_ATTRIB_FILTER = {'name', 'address', 'portNumber', 'NATPrivateAddress'}

def apa_to_med(
    input_path: str | bytes,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    # Application-specific handling for *.APA files that
    # keeps streams in memory.
    #
    # Just a placeholder function for exploration for now
    with olefile.OleFileIO(input_path) as ole:
        streams = decompress.decompress_archive(
            ole=ole,
            progress=progress
        )
        return streams
    
def apa_to_med_folder(
    input_path: str | bytes, 
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    # Application-specific handling for *.APA files that
    # writes streams to a folder.
    #
    # Just a placeholder function for exploration for now
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = apa_to_med(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        stream_output_path = decompress._create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)

def mer_to_med(
    input_path: str | bytes,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    # Application-specific handling for *.MER files that
    # keeps streams in memory.
    #
    # Just a placeholder function for exploration for now
    with olefile.OleFileIO(input_path) as ole:
        streams = decompress.decompress_archive(
            ole=ole,
            progress=progress
        )
        return streams
    
def mer_to_med_folder(
    input_path: str | bytes,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    # Application-specific handling for *.MER files that
    # writes streams to a folder.
    #
    # Just a placeholder function for exploration for now
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = mer_to_med(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        stream_output_path = decompress._create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)

def _mer_get_shortcut_names(
    streams: list[types.MEArchive],
) -> list[tuple[str, str]]:
    file = 'RSLinx Enterprise/SCLocal.xml'
    try:
        xml = util._get_stream_by_name(streams, file).data.decode('utf-16-le')
    except Exception as e:
        raise FileNotFoundError(f'{file} was not found.  Shortcuts may not exist.')

    root = ET.fromstring(xml)
    shortcuts = []
    for shortcut in root.findall('shortcut'):
        name = shortcut.attrib.get('name')
        device = shortcut.attrib.get('device')
        shortcuts.append((name, device))
    return shortcuts

def _mer_filter_shortcut_attributes(element: ET.Element, whitelist: list[str]) -> ET.Element:
    # Create a new Element with the same tag
    filtered_node = ET.Element(element.tag)

    # Copy only specific attributes
    for attr in whitelist:
        if attr in element.attrib:
            filtered_node.set(attr, element.attrib[attr])

    return filtered_node

def _mer_get_device_nodes(topology: ET.Element, node1: str, node2: str) -> list[ET.Element]:
    parent_map = {child: parent for parent in topology.iter() for child in parent}
    for device in topology.findall(".//device[@name='" + node2 + "']"):
        current = device
        path_nodes = []
        found_node1 = False
        while current is not None:
            name = current.attrib.get("name")
            if name:
                path_nodes.insert(0, current)
                if name == node1:
                    found_node1 = True
            current = parent_map.get(current)
        if found_node1:
            return path_nodes
    return []

def _mer_get_shortcut_nodes(
    streams: list[types.MEArchive],
    shortcuts: list[tuple[str, str]]
) -> list[tuple[str, list[ET.Element]]]:
    file = 'RSLinx Enterprise/RSLinxNG.xml'
    try:
        xml = util._get_stream_by_name(streams, 'RSLinx Enterprise/RSLinxNG.xml').data.decode('utf-16-le')
    except Exception as e:
        raise FileNotFoundError(f'{file} was not found.  Shortcuts may not exist.')

    root = ET.fromstring(xml)
    topology = root.find("Topology")
    result = []
    for shortcut_name, device_string in shortcuts:
        if '.' not in device_string:
            result.append((shortcut_name, ""))
            continue
        node1, node2 = device_string.split('.', 1)
        path = _mer_get_device_nodes(topology, node1, node2)
        result.append((shortcut_name, path))

    return result

def _mer_print_shortcut_nodes(
    shortcut: str,
    nodes: list[ET.Element]
):
    print(f'Shortcut {shortcut} Topology:')
    for i, line in enumerate(nodes):
        # Determine prefix based on position
        if i == len(nodes) - 1:
            connector = "└── "
        else:
            connector = "├── "
        
        # Build indentation
        indent = "│   " * i
        print(f"{indent}{connector}{line}")

def mer_get_shortcuts(
    input_path: str | bytes,
    print_summary: bool = False,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[tuple[str, list[ET.Element]]]:
    
    # Application-specific function for *.MER files to
    # get the list of communications shortcuts    
    streams = mer_to_med(
        input_path=input_path,
        progress=progress
    )
    shortcuts = _mer_get_shortcut_names(streams)
    paths = _mer_get_shortcut_nodes(streams, shortcuts)
    for (name, path) in paths:
        filtered_nodes = []
        for node in path:
            filtered_node =_mer_filter_shortcut_attributes(node, MER_FTLINX_ATTRIB_FILTER)
            filtered_nodes.append(ET.tostring(filtered_node, encoding='unicode'))
        if print_summary: _mer_print_shortcut_nodes(name, filtered_nodes)

    return paths

def _mer_rewrite_checksum(
    input_path: str,
    output_path: str
) -> bytes:
    # Read file and calculate checksum
    file_data = bytes()
    with open(input_path, 'rb') as f:
        raw_data = f.read()
        file_data = raw_data[:-4]
    new_checksum = util.crc32_checksum(file_data).to_bytes(length=4, byteorder='little', signed=False)
    file_data = file_data + new_checksum

    # Re-write file with updated checksum
    with open(output_path, 'wb') as f:
        f.write(file_data)

    return new_checksum

def mer_unlock(
    input_path: str,
    output_path: str,
):
    # Create copy of *.MER file to work with
    if not(os.path.exists(os.path.dirname(output_path))): os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy(input_path, output_path)

    # Edit the contents of FILE_PROTECTION
    with olefile.OleFileIO(output_path, write_mode=True) as ole:
        stream = bytearray(ole.openstream('FILE_PROTECTION').read())
        msb = len(stream)

        if (msb < 7): raise FileNotFoundError(f'Unexpected file size {msb} for FILE_PROTECTION, cannot proceed.')
        stream[0] = 0x00 # No Password
        stream[1] = 0x03 # Length LSW?
        stream[2] = 0x00 # Length MSW?
        stream[3] = 0x00 # Allow Convert
        for i in range(4,msb):
            stream[i] = 0x00 # Remaining content would be password.

        ole.write_stream('FILE_PROTECTION', bytes(stream))

    # Re-rewrite the checksum of the *.MER copy in place
    _mer_rewrite_checksum(input_path=output_path, output_path=output_path)

def apa_unlock(
    input_path: str,
    output_path: str
):
    # Create copy of *.APA file to work with
    if not(os.path.exists(os.path.dirname(output_path))): os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy(input_path, output_path)

    # Edit the contents of FTSPHasPwd
    with olefile.OleFileIO(output_path, write_mode=True) as ole:
        stream = bytearray(ole.openstream('FTSPHasPwd').read())
        msb = len(stream)

        if (msb < 4): raise FileNotFoundError(f'Unexpected file size {msb} for FTSPHasPwd, cannot proceed.')
        stream[0] = 0x00 # No Password
        ole.write_stream('FTSPHasPwd', bytes(stream))
