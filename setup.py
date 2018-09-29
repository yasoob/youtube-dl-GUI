from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

from distutils.sysconfig import get_python_lib
site_packages_path = get_python_lib()
plugins_path = os.path.join(site_packages_path, 'PyQt4', 'plugins', 'imageformats')
image_format_dlls = map(
    lambda dll: os.path.join(plugins_path, dll),
    ['qjpeg4.dll', 'qgif4.dll', 'qico4.dll', 'qmng4.dll', 'qsvg4.dll', 'qtiff4.dll']
)

DATA=[('imageformats', image_format_dlls), ('', ['.\\ffmpeg.exe'])]

for files in os.listdir(os.path.join(os.getcwd(),'UI')):
    f1 = os.path.join(os.getcwd(),'UI', files)
    if os.path.isfile(f1): # skip directories
        f2 = 'UI', [f1]
        DATA.append(f2)

setup(
    options = {'py2exe': {'compressed': True,"includes":["sip"]}},
    windows = [{
                   'script': "main.py",
                   "icon_resources": [(0, os.path.join(os.getcwd(),"resources","converted_icon.ico"))],
                   "dest_base":"youtube-gl",
               }],
    zipfile = None,
    data_files = DATA,
)
