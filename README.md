youtube-dl-GUI
==============

This repository contains code for a youtube-dl GUI written in PyQt. It is based on [youtube-dl](https://github.com/rg3/youtube-dl) which is a Video downloading script maintained by various contributers and released in Public Domain. This GUI code is currently written for Python v2.x and not v3.x However I will make it compatible with Python v3.x after refining it a little. Please note that this GUI code is released under the MIT License and not Public Domain.

ScreenShot:
-------------
![youtube-dl-gui Screenshot in Ubuntu](http://imgur.com/EJ1krDt.png)

Requirements:
------------
- PyQt4
- Python >= v2.6
- py2exe - _see Windows_

Features:
----------
This application has the following features:
- supports downloading videos from 200+ websites
- allows to download multiple videos in parallel
- shows download statistics separately for each video
- Resumes interrupted downloads
- Downloads the video in best quality

Windows:
-----------
The exe is currently hosted on [Dropbox](https://www.dropbox.com/s/oj8dh4q82tofk34/youtube-dl.exe). I have included a setup.py file. Just run it like this:
```
python setup.py py2exe
```
This will result in a dist and build directory. Simply go to the dist directory and you will get a ```main.exe``` file and some other files. That ```main.exe``` file is a standalone executable which can be run simply by double clicking it. You can distribute that file to your friend.

Contributor:
---------
- Muhammad Yasoob Ullah Khalid

If you want to become a contributor then just contribute some code and I will add you to this list

Bugs:
----------
This program is still in beta so if you encounter any bugs feel free to report them on https://github.com/yasoob/youtube-dl-GUI/issues. 

TODO:
-------
- Allow pause/resume functionality
- integrate post processing options
- integrate batch add feature
- integrate save state
- integrate Queue to make it stable

License:
----------
This project is released under the MIT license. See the included license file.
