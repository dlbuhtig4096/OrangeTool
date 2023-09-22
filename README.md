
# Introduction #
This is a python library for processing game archives from the **OrangeClient**.

# Modules #

## arc.py ##
This module processes streaming assets.

 - `procUnpack`: Unpack the download data under the stream assets.
    - Argments:
        - `str dst`: The folder to decrypted assets.
        - `str src`: The folder to encrypted assets.
        - `list<OrangeTool.NullLdr> ldr`: List of loaders.
        - `set<str> ls`: Set of str of processed files.
    - Return value:
        - `void`: None.

 - `procRepack`: Repack the download data under the stream assets.
    - Argments:
        - `str dst`: The folder to decrypted assets.
        - `str src`: The folder to encrypted assets.
        - `list<OrangeTool.NullLdr> ldr`: List of loaders.
        - `set<str> ls`: Set of str of processed files.
    - Return value:
        - `void`: None.

 - `procCrawl`: Crawl download data from the online server.
     - Argments:
        - `str dst`: The folder to decrypted assets.
        - `str src`: The folder to encrypted assets.
        - `list<OrangeTool.NullLdr> ldr`: Unused.
        - `set<str> ls`: Unused.
    - Return value:
        - `void`: None.

## net.py ##
This module processes raw payloads from the server responses.

 - `procDecode`: Decode the response body from the server.
    - Argments:
        - `str dst`: Destination folder.
        - `str src`: Source folder.
    - Return value:
        - `void`: None.

## save.py ##
This module processes save files from offline game.

 - `bfDecode`: Decode the brief file to memory.
    - Argments:
        - `dict data`: Output data.
        - `io.IOBase hwd`: Input file handle.
    - Return value:
        - `dict`: The decoded file metadata from the file handle.

 - `bfEncode`: Encode the brief file from memory.
    - Argments:
        - `dict data`: Input data.
        - `io.IOBase hwd`: Output file handle.
    - Return value:
        - `bytes`: Encoded data.
    
 - `sdDecode`: Decode save data to memory.
    - Argments:
        - `dict data`: Output data.
        - `io.IOBase hwd`: Input file handle.
    - Return value:
        - `dict`: The decoded file metadata from the file handle.

 - `sdEncode`: Encode save data from memory.
    - Argments:
        - `dict data`: Input data.
        - `io.IOBase hwd`: Output file handle.
    - Return value:
        - `bytes`: Encoded data.

 - `procDecode`: Decode save directory on the file system.
    - Argments:
        - `str brief`: Name of the brief file, usually the smallest file under the save folder.
        - `str rt`: Path to the save folder.
    - Return value:
        - `void`: None.

 - `procEncode`: Encode save directory on the file system.
    - Argments:
        - `str brief`: Name of the brief file, usually the smallest file under the save folder.
        - `str rt`: Path to the save folder.
    - Return value:
        - `void`: None.

# Credits #
 - **[DarkDunterX](https://github.com/DarkHunterX)** for his detailed researches on file archives.
 - **Blues** for his save dump from the online game.
