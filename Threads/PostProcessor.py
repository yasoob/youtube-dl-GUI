__author__ = 'Yasoob'
from youtube_dl.postprocessor.ffmpeg import FFmpegPostProcessor
from PyQt4 import QtCore
import os
import math


class FFmpegVideoConvertorPP(FFmpegPostProcessor):
    def __init__(self, outpath, downloader=None, preferedformat=None):
        super(FFmpegVideoConvertorPP, self).__init__(downloader)
        self._preferedformat = preferedformat
        self.outpath = outpath

    def run(self, information):
        path = information['filepath']
        self.outpath = os.path.join(self.outpath, os.path.split(path)[-1])
        if information['ext'] == self._preferedformat:
            return True, information
        prefix, sep, ext = path.rpartition('.')

        print path
        print self.outpath
        print self._preferedformat
        print prefix + sep + self._preferedformat
        print "\n"

        self.run_ffmpeg(path, self.outpath, [])
        information['filepath'] = self.outpath
        information['format'] = self._preferedformat
        information['ext'] = self._preferedformat
        return False, information

class DummyDownloader(object):
    params = {}

    def to_screen(self, e):
        pass


class PostProcessor(QtCore.QThread):
    """
    preferred_format
    filepath
    ext
    format
    """
    statusSignal = QtCore.pyqtSignal(QtCore.QString)
    list_Signal = QtCore.pyqtSignal([list])
    row_Signal = QtCore.pyqtSignal()
    error_occurred = False
    done = False

    def __init__(self, opts):
        super(PostProcessor, self).__init__(opts.get('parent'))
        self.preferred_format = opts.get('preferred_format')
        self.convertor = FFmpegVideoConvertorPP(opts.get('out_path'), preferedformat=self.preferred_format)
        self.convertor._deletetempfiles = opts.get('delete_tmp')
        self.convertor._downloader = DummyDownloader()
        self.file_path = opts.get('file_path')
        self.local_rowcount = opts.get('row_count')
        self.speed = '-- KiB/s'
        self.bytes = self.format_bytes(os.path.getsize(self.file_path))
        self.eta = "00:00"
        self.ext = self.file_path.split('.')[-1]

    def convert(self):
        #try:
        result = self.convertor.run({
            "ext": self.ext,
            "filepath": unicode(self.file_path),
        })
        return result

    def run(self):
        self.list_Signal.emit([
            self.local_rowcount,
            os.path.split(self.file_path)[-1].split('.')[0],
            self.bytes,
            self.eta,
            self.speed,
            'Converting'
        ])
        self.convert()
        self.list_Signal.emit([
            self.local_rowcount,
            os.path.split(self.file_path)[-1].split('.')[0],
            self.bytes,
            self.eta,
            self.speed,
            'Finished'
        ])

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