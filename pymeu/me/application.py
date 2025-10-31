from collections.abc import Callable
import olefile
import os
import shutil
from typing import Optional
import xml.etree.ElementTree as ET

from . import decompress
from . import enums
from . import primitives
from . import types
from . import util

MER_FTLINX_ATTRIB_FILTER = {'name', 'address', 'portNumber', 'NATPrivateAddress'}

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

def _mer_get_shortcut_names(
    streams: list[types.MEArchive],
) -> list[tuple[str, str]]:
    file = 'RSLinx Enterprise/SCLocal.xml'
    try:
        xml = util._get_stream_by_name_exact(streams, file).data.decode('utf-16-le')
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
        xml = util._get_stream_by_name_exact(streams, 'RSLinx Enterprise/RSLinxNG.xml').data.decode('utf-16-le')
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
    streams = decompress.archive_to_stream(
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

def _recipeplus_get_config(
    streams: list[types.MEArchive],
) -> types.MERecipePlusConfig:
    raw = util._get_stream_by_name_exact(streams, 'Config')
    bin = types.MEBinStream(
        data=raw.data,
        offset=0
    )
    primitives._seek_forward(input=bin, length=12)
    runtime_recipe_name = primitives._seek_string_var_len(input=bin)
    status_tag = primitives._seek_string_var_len(input=bin)
    percent_complete_tag = primitives._seek_string_var_len(input=bin)
    primitives._seek_forward(input=bin, length=4)
    runtime_recipe_name_tag = primitives._seek_string_var_len(input=bin)
    result = types.MERecipePlusConfig(
        runtime_recipe_name=runtime_recipe_name,
        status_tag=status_tag,
        percent_complete_tag=percent_complete_tag,
        runtime_recipe_name_tag=runtime_recipe_name_tag
    )
    return result

def _recipeplus_get_data_sets(
    streams: list[types.MEArchive],
) -> list[types.MERecipePlusTagSet]:
    result = []
    data_sets_raw = util._get_streams_by_name_prefix(streams, 'DataSets/')
    for data_set in data_sets_raw:
        data_set_values = _recipeplus_deserialize_value_list(data_set)
        result.append(types.MERecipePlusDataSet(
            name=data_set.path[-1],
            value=data_set_values
        ))
    return result

def _recipeplus_get_decimal_places(
    streams: list[types.MEArchive],
) -> list[int]:
    decimals_raw = util._get_stream_by_name_exact(streams, 'Decimals')
    result = _recipeplus_deserialize_value_list(decimals_raw)
    return result

def _recipeplus_get_data_value(input: types.MEBinStream):
    datatype = enums.MERecipePlusDataType(primitives._seek_int(input=input, length=2))
    value = None
    match datatype:
        case enums.MERecipePlusDataType.NoType:
            pass
        case enums.MERecipePlusDataType.Int16:
            value = primitives._seek_int(input=input, length=2)
        case enums.MERecipePlusDataType.Int32:
            value = primitives._seek_int(input=input)
        case enums.MERecipePlusDataType.Fp32:
            value = primitives._seek_float(input=input)
        case enums.MERecipePlusDataType.Fp64:
            value = primitives._seek_double(input=input)
        case enums.MERecipePlusDataType.String:
            value = primitives._seek_string_var_len(input=input)
        case enums.MERecipePlusDataType.UInt16:
            value = primitives._seek_int(input=input, length=2, signed=False)
        case enums.MERecipePlusDataType.UInt32:
            value = primitives._seek_int(input=input, signed=False)
        case _:
            raise NotImplementedError(f'Data type {datatype} not implemented at offset {input.offset:0X}.')

    return value

def _recipeplus_get_ingredients(
    streams: list[types.MEArchive],
) -> list[types.MERecipePlusIngredient]:
    result = []
    raw = util._get_stream_by_name_exact(streams, 'Ingredients')
    bin = types.MEBinStream(
        data=raw.data,
        offset=0
    )
    header_len = primitives._lookahead_int(input=bin)
    primitives._seek_forward(input=bin, length=header_len)
    while (bin.offset < len(bin.data)):
        ingredient_type = primitives._seek_int(input=bin)
        min = _recipeplus_get_data_value(input=bin)
        max = _recipeplus_get_data_value(input=bin)
        name = primitives._seek_string_var_len(input=bin)
        result.append(types.MERecipePlusIngredient(
            name=name,
            type=enums.MERecipePlusIngredientType(ingredient_type),
            min=min,
            max=max
        ))
    return result

def _recipeplus_get_tag_sets(
    streams: list[types.MEArchive],
) -> list[types.MERecipePlusTagSet]:
    result = []
    tag_sets_raw = util._get_streams_by_name_prefix(streams, 'TagSets/')
    for tag_set in tag_sets_raw:
        tag_set_values = _recipeplus_deserialize_string_list(tag_set)
        result.append(types.MERecipePlusTagSet(
            name=tag_set.path[-1],
            value=tag_set_values
        ))
    return result

def _recipeplus_get_units(
    streams: list[types.MEArchive],
) -> list[types.MERecipePlusUnit]:
    result = []
    raw = util._get_stream_by_name_exact(streams, 'Units')
    bin = types.MEBinStream(
        data=raw.data,
        offset=0
    )
    header_len = primitives._lookahead_int(input=bin)
    primitives._seek_forward(input=bin, length=header_len)
    while(bin.offset < len(bin.data)):
        name = primitives._seek_string_var_len(input=bin)
        id = primitives._seek_string_var_len(input=bin)
        data_set = primitives._seek_string_var_len(input=bin)
        tag_set = primitives._seek_string_var_len(input=bin)
        result.append(types.MERecipePlusUnit(
            name=name,
            id=id,
            data_set=data_set,
            tag_set=tag_set
        ))
    return result

def _recipeplus_deserialize_stream(
    stream: types.MEArchive,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> types.MERecipePlusFile:
    with olefile.OleFileIO(bytes(stream.data)) as ole:
        recipe_streams = decompress.decompress_archive(
            ole=ole,
            progress=progress
        )
        config = _recipeplus_get_config(streams=recipe_streams)
        ingredients = _recipeplus_get_ingredients(streams=recipe_streams)
        decimal_places = _recipeplus_get_decimal_places(streams=recipe_streams)
        data_sets = _recipeplus_get_data_sets(streams=recipe_streams)
        tag_sets = _recipeplus_get_tag_sets(streams=recipe_streams)
        units = _recipeplus_get_units(streams=recipe_streams)

        return types.MERecipePlusFile(
            config=config,
            ingredients=ingredients,
            decimal_places=decimal_places,
            data_sets=data_sets,
            tag_sets=tag_sets,
            units=units
        )

def recipeplus_deserialize(
    input_path: str | bytes,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MERecipePlusFile]:
    # Application-specific function for *.MER files to
    # get RecipePlus data
    streams = decompress.archive_to_stream(
        input_path=input_path,
        progress=progress
    )
    recipe_streams = util._get_streams_by_name_prefix(streams, 'RecipePlus/')
    result = []
    for recipe_stream in recipe_streams:
        result.append(_recipeplus_deserialize_stream(stream=recipe_stream, progress=progress))
    return result

def _recipeplus_deserialize_value_list(
    stream: types.MEArchive        
) -> list:
    result = []
    bin = types.MEBinStream(
        data=stream.data,
        offset=0
    )
    header_len = primitives._lookahead_int(input=bin)
    primitives._seek_forward(input=bin, length=header_len)
    while (bin.offset < len(bin.data)):
        result.append(_recipeplus_get_data_value(input=bin))

    return result

def _recipeplus_deserialize_string_list(
    stream: types.MEArchive        
) -> list:
    result = []
    bin = types.MEBinStream(
        data=stream.data,
        offset=0
    )
    header_len = primitives._lookahead_int(input=bin)
    primitives._seek_forward(input=bin, length=header_len)
    while (bin.offset < len(bin.data)):
        result.append(primitives._seek_string_var_len(input=bin))

    return result


def recipeplus_to_folder(
    input_path: str | bytes,
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    # Application-specific function to get raw
    # RecipePlus files extracted from *.MER/*.APA files
    streams = decompress.archive_to_stream(
        input_path=input_path,
        progress=progress
    )
    recipes = util._get_streams_by_name_prefix(streams, 'RecipePlus/')
    for recipe in recipes:
        with olefile.OleFileIO(bytes(recipe.data)) as ole:
            streams = decompress.decompress_archive(
                ole=ole,
                progress=progress
            )
            for stream in streams:
                recipe_path = []
                recipe_path.append(os.path.splitext(recipe.path[-1])[0])
                for path in stream.path: recipe_path.append(path)
                stream_output_path = decompress._create_subfolders(output_path, recipe_path)
                with open(stream_output_path, 'wb') as f:
                    f.write(stream.data)