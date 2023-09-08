
# Introduction #
This is a python library for the **OrangeClient**.

# Modules #

## save.py ##
This module encodes the offline save.

 - `metaDecode`: Decode metadata to memory.
    - Argments:
        - `dict data`: Output data.
        - `io.IOBase hwd`: Input file handle.
    - Return value:
        - `dict`: The decoded file metadata from the file handle.

 - `metaEncode`: Encode metadata from memory.
    - Argments:
        - `dict data`: Input data.
        - `io.IOBase hwd`: Output file handle.
    - Return value:
        - `bytes`: Encoded data.
    
 - `slotDecode`: Decode save slot to memory.
    - Argments:
        - `dict data`: Output data.
        - `io.IOBase hwd`: Input file handle.
    - Return value:
        - `dict`: The decoded file metadata from the file handle.

 - `slotEncode`: Encode save slot from memory.
    - Argments:
        - `dict data`: Input data.
        - `io.IOBase hwd`: Output file handle.
    - Return value:
        - `bytes`: Encoded data.

 - `procDecode`: Decode save directory on the file system.
    - Argments:
        - `str rt`: Path to the save folder.
        - `str meta`: Name to the metadata, usually the smallest file under the save folder.
    - Return value:
        - `void`: None.

 - `procEncode`: Encode save directory on the file system.
    - Argments:
        - `str rt`: Path to the save folder.
        - `str meta`: Name to the metadata, usually the smallest file under the save folder.
    - Return value:
        - `void`: None.

## payload.py ##
This module decodes payload from the online packets.

 - `procDecode`: Decode the response body from the server.
    - Argments:
        - `str dst`: Destination folder.
        - `str src`: Source folder.
    - Return value:
        - `void`: None.


