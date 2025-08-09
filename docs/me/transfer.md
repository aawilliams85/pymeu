# ME Transfer Notes

## High Level Explanation
The file transfer process used to upload/download files from an ME terminal is all based upon CIP messaging, hence why it can be performed directly or routed across other CIP devices.  The basic process is to create a transfer instance, transfer the file chunk by chunk, and then delete the transfer instance. 

##  Lexicon
| Term              | Description
|-------------------|------------
| Chunk             | One block of potentially multiple blocks of data that together form a file.
| Transfer Instance | A pipe use to read chunks from, or write chunks to, a terminal.

## Transfer Instance
The request to create a file transfer consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00      | Transfer Type (0x00 = Upload From Terminal, 0x01 = Download To Terminal)
| 0x01      | Overwrite (0x00 = New File, 0x01 = Overwrite Existing File)
| 0x02-0x03 | Chunk size in bytes
| 0x04+     | File name, null terminated (0x00)

The response consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x01 | Message Instance
| 0x02-0x03 | Unknown (message instance MSW?)
| 0x04-0x05 | Transfer Instance (use this instance number for the file chunks)
| 0x06-0x07 | Chunk size in bytes
| 0x08-0x11 | File size in bytes (if Transfer Type is Upload, otherwise not present)

## Upload File
## Download File
## MER Files