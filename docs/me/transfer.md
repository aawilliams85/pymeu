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
When uploading from a terminal, the file is read in chunks of the size specified by the Transfer Instance.
The request consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x03 | Chunk number

The response consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x03 | Unknown
| 0x04-0x07 | Chunk number echo
| 0x08-0x09 | Chunk size in bytes
| 0x10+     | Chunk data

Note that the last chunk is typically going to be an irregular size.
Finally, a response of chunk 0, chunk size 2, chunk data 0xFFFF indicates end-of-file.

## Download File
When downloading to a terminal, the file is written in chunks of the size specified by the Transfer Instance.
The request consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x03 | Chunk number
| 0x04-0x05 | Chunk size in bytes
| 0x06+     | Chunk data

The response consists of the following byte structure:

| Bytes     | Purpose
|-----------|----------
| 0x00-0x03 | Unknown
| 0x04-0x07 | Chunk number echo
| 0x08-0x11 | Next chunk number expected

Note that the last chunk is typically going to be an irregular size.
Finally, a request of 0x000000000200FFFF indicates end-of-file.

Note that there are edge cases (firmware upgrade of v6+ terminals) where the terminal withholds a response for an extended time.  The progress bar remains empty for a while as chunks are transferred; when it starts moving, it has reached the point where the response is being withheld.  After the progress bar stops moving again, it continues.  There seems to be three times during a typical v6+ firmware update that this happens.  If the socket breaks, the flash fails and a factory reset is required.

## MER Files