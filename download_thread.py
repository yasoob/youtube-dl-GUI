import math
from PyQt4 import QtGui
from PyQt4 import QtCore
import youtube_dl
import time

class Download(QtCore.QThread):
    statusSignal = QtCore.pyqtSignal(QtCore.QString)
    remove_url_Signal = QtCore.pyqtSignal(str)
    list_Signal = QtCore.pyqtSignal([list])
    row_Signal = QtCore.pyqtSignal()
    error_occured = False

    def __init__(self,url,directory,rowcount):
        super(Download,self).__init__()
        self.url = url
        self.directory = directory
        self.local_rowcount = rowcount
        if self.directory is not '':
            self.directory = directory + '/'

    def hook(self, li):
        if li.get('downloaded_bytes') is not None:
            #self.p_barSignal.emit(int((float(li.get('downloaded_bytes')) / float(li.get('total_bytes')))*100.0))
            if li.get('speed') is not None:
                self.speed = self.format_speed(li.get('speed'))
                self.eta = self.format_seconds(li.get('eta'))
                self.list_Signal.emit( [self.local_rowcount, li.get('filename').split('/')[-1],self.eta,self.speed,li.get('status')])
            elif li.get('status') == "finished":
                self.remove_url_Signal.emit(self.url)
                self.list_Signal.emit( [self.local_rowcount, li.get('filename').split('/')[-1],self.eta,self.speed,li.get('status')])
        else:
            self.statusSignal.emit('Already Downloaded')
            self.row_Signal.emit()
            self.remove_url_Signal.emit(self.url)
            time.sleep(10)
            return
        if li.get('eta') is not None:
            filename = li.get('filename').split('/')[-1][:25]+'..'

    def download(self):
        ydl_options = {
            'outtmpl': '{0}%(title)s-%(id)s.%(ext)s'.format(self.directory),
            'continuedl': True,
            'quiet' : True,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.add_default_info_extractors()
            ydl.add_progress_hook(self.hook)
            try:
                ydl.download([self.url])        
            except (youtube_dl.utils.DownloadError,youtube_dl.utils.ContentTooShortError,youtube_dl.utils.ExtractorError) as e:
                self.row_Signal.emit()
                self.error_occured = True
                self.statusSignal.emit(str(e))
        #self.p_barSignal.emit(0)

    def run(self):
        self.download()
        if self.error_occured is not True:
            self.statusSignal.emit('Done!')

    def format_seconds(self,seconds):
        (mins, secs) = divmod(seconds, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            return '--:--:--'
        if hours == 0:
            return '%02d:%02d' % (mins, secs)
        else:
            return '%02d:%02d:%02d' % (hours, mins, secs)

    def format_bytes(self,bytes):
        if bytes is None:
            return u'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = [u'B', u'KiB', u'MiB', u'GiB', u'TiB', u'PiB', u'EiB', u'ZiB', u'YiB'][exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return u'%.2f%s' % (converted, suffix)

    def format_speed(self,speed):
        if speed is None:
            return '%10s' % '---b/s'
        return '%10s' % ('%s/s' % self.format_bytes(speed))