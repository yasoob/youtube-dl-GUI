# youtube-dl-GUI

This repository contains code for a youtube-dl GUI written in PyQt. It is based on [youtube-dl](https://github.com/ytdl-org/youtube-dl) which is a Video downloading script maintained by various contributers and released in Public Domain. This GUI code is currently written for Python v3.x. Please note that this GUI code is released under the MIT License and not Public Domain.

## ScreenShot:

![youtube-dl-gui Screenshot in Ubuntu](http://imgur.com/KxTLeYl.png)

## Requirements:

- PyQt5
- [youtube_dl](https://github.com/ytdl-org/youtube-dl)
- Python >= v3.x

## Features:

This application has the following features:
- supports downloading videos from 200+ websites
- allows to download multiple videos in parallel
- shows download statistics separately for each video
- Resumes interrupted downloads
- Downloads the video in best quality

## Contributor:

- Muhammad Yasoob Ullah Khalid
- Oleksis Fraga <oleksis.fraga@gmail.com>

If you want to become a contributor then just contribute some code and I will add you to this list

## Bugs:

This program is still in beta so if you encounter any bugs feel free to report them on https://github.com/yasoob/youtube-dl-GUI/issues.

## TODO:

- Fix Convert (main:MainWindow.convert_file)
- integrate save state
- Allow pause/resume functionality
- ~~integrate post processing options~~
- ~~integrate batch add feature~~
- ~~integrate Queue to make it stable~~
- ~~Change for PyInstaller: setup.py - _see Windows_~~

## Windows:

Run the setup.py file like this:

```bash
python setup.py pyinstaller
```

This will result in a **dist** and **build** directory. Simply go to the **dist** directory and you will get a ```youtube-dl-gui.exe``` file and some other files. That ```youtube-dl-gui.exe``` file is a standalone executable which can be run simply by double clicking it. You can distribute that file to your friend.

## License:

This project is released under the MIT license. See the included license file.
