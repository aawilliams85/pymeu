from collections.abc import Callable
import olefile
import os
from typing import Optional

from . import decompress
from . import types

def apa_to_med(
    input_path: str,
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
    input_path: str, 
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
    input_path: str,
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
    input_path: str,
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