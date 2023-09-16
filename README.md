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
