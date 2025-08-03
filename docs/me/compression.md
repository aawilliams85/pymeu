# ME Compression Notes

## High Level Explanation
Inside an ME file (work targeted at *.FUP, may apply to *.APA, *.MER, and others) streams have some additional formatting that needs to be handled to extract them back into the expected files.  Many are also compressed with what seems to be some sort of LZ-based algorithm.  Some of this work is incomplete, but functional enough to decompress the files that have been tested so far.

##  Lexicon
There is no officially provided frame-of-reference for interpreting the compressed streams inside some ME files, so this is an attempt to disambiguate them.

| Term        | Description
|-------------|------------
| Stream      | One file stream inside the OLE container (i.e. the *.FUP file).
| Page        | One block of potentially multiple blocks of data that together form the original file.  May be compressed or uncompressed.
| Chunk       | One block of potentially multiple blocks of data that together form a page.  In the compressed form, there are a fixed number of tokens per chunk.
| Token       | One piece of data within a chunk.  In the compressed form, each token can be a literal byte value, or a pointer.  In the decompressed form, each token is a literal byte value.

## Page Structure
A file stream inside the ME file typically structured as:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x03 | Page size to follow (in bytes)
| 0x04      | Page compression control byte (0x00 = Compressed, 0x01 = Uncompressed)
| 0x05      | Unknown
| 0x06      | Unknown
| 0x07      | Unknown
| 0x08+     | Page data (starting with first chunk)

If the stream is large enough to have more than one page, the structure above repeats.

## Chunk Structure
Each chunk inside the page is made up of a fixed number of tokens.  There are 2 control bytes, followed by 16 tokens.  Then the pattern repeats.<br>
The control bytes are used bitwise to determine whether a given token is a literal byte value, or a pointer (0 indicates a literal, 1 indicates a pointer).

## Pointer Structure
If a token is a pointer, it is made up of 2 bytes.<br>
| Byte                | Purpose
|---------------------|---------
| 0x00 (lower nibble) | (Length - 1) of original data.
| 0x00 (upper nibble) | Offset MSB
| 0x01                | Offset LSB

The way the decompression works, each pointer token will look back the OFFSET number of bytes into the decompressed stream and copy the LENGTH number of bytes in.  Given a single nibble is used for (Length - 1) this means a maximum of 16 bytes can be restored from one pointer.<br><br>

If the length is greater than the offset, the decompressed stream for a given pointer can become part of the decompression.<br>
If the offset is zero, it is a special case where the last byte before this pointer is copied repeatedly to satisfy the length.