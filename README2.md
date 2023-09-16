
# Introduction #
This is a python library for processing game archives from the **OrangeClient**.

# Modules #

## arc.py ##
This module processes streaming assets.

 - `procUnpack`: Unpack the download data under the stream assets.
    - Argments:
        - `str dst`: Work directory.
        - `str src`: The StreamingAssets folder.
        - `*ls`: Optional additional arguments, str of processed files.
    - Return value:
        - `void`: None.

 - `procRepack`: Repack the download data under the stream assets.
    - Argments:
        - `str dst`: Work directory.
        - `str src`: The StreamingAssets folder.
        - `*ls`: Optional additional arguments, str of processed files.
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

This is a python library for processing game archives.
Repository: https://github.com/dlbuhtig4096/OrangeTool

Dependency
You would be able to install all dependency via pip install -r requirements.txt.

Usage
save.py
save.py [mode] [brief] [root]
[mode] = d for decode, e for encode.
[brief] = The filename of brief in your save, usually it is the smallest one.
[root] = Optional, the root to your save, usually %LOCALAPPDATA%Low\CAPCOM\ROCKMAN X DiVE Offline for steam version.
For example, python save.py d brief "%LOCALAPPDATA%Low\CAPCOM\ROCKMAN X DiVE Offline"
In case you don't want python, you may use the compiled binary by @DarkHunter.

net.py
net.py [dst] [src]
[dst] = Output folder.
[src] = The folder to raw response bodies / decrypted payloads.
[crypto] = Optional, put any characters when the save if raw response.
This tool decrypts save dumps from online game.

arc.py
arc.py [mode] [dst] [src] [...list]
[mode] = d for unpack, e for repack.
[dst] = Working directory.
[src] = Path to Game_Data\StreamingAssets\DownloadData.
[list] = Optional. When specified, the program would only process the files in list.
This tool processes archives under the DownloadData, e.g.,
python arc.py d .\out .\src  unpacks everything from .\src to .\out.
python arc.py d .\out .\src GameData.bin  unpacks GameData.bin from .\DownloadData to .\out.
python arc.py d .\out .\src abconfig 824dd5b6077030962439aaee4818a52b  unpacks .\DownloadData\824dd5b6077030962439aaee4818a52b to .\out\stage/prefab/oldcastle/object/prefabs/floor06_002.
