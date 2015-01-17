from distutils.core import setup
import py2exe, sys, os

sys.argv.append('py2exe')

DATA=[('imageformats',[
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll',
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll',
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll',
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qmng4.dll',
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll',
    'C:\Users\yasoob\Anaconda\Lib\site-packages\PyQt4\plugins\imageformats\qtiff4.dll',
]), ('', ['C:\Users\yasoob\Documents\GitHub\youtube-dl-GUI\\ffmpeg.exe'])]

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