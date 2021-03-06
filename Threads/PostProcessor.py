import os
import math

from youtube_dl.postprocessor.ffmpeg import FFmpegPostProcessor
from PyQt5 import QtCore


class FFmpegVideoConvertorPP(FFmpegPostProcessor):
    def __init__(self, outpath, downloader=None, preferedformat=None):
        super(FFmpegVideoConvertorPP, self).__init__(downloader)
        self._preferedformat = preferedformat
        self.outpath = outpath

    def run(self, information):
        path = information['filepath']
        file_name = os.path.split(path)[-1]
        self.outpath = os.path.join(self.outpath, file_name)

        if information['ext'] == self._preferedformat:
            return True, information
        
        prefix, sep, ext = self.outpath.rpartition('.')
        self.outpath = prefix + sep + self._preferedformat

        self.run_ffmpeg(path, self.outpath, [])
        information['filepath'] = self.outpath
        information['format'] = self._preferedformat
        information['ext'] = self._preferedformat
        return False, information

class DummyDownloader(object):
    params = {}

    def to_screen(self, e):
        pass


class PostProcessorSignals(QtCore.QObject):
    "Define the signals available from a running postprocessor thread"

    statusBar_Signal = QtCore.pyqtSignal(str)
    list_Signal = QtCore.pyqtSignal([list])
    row_Signal = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

class PostProcessor(QtCore.QRunnable):
    "PostProcessor Thread"

    def __init__(self, opts):
        super(PostProcessor, self).__init__()
        self.parent = opts.get('parent')
        self.error_occurred = False
        self.done = False
        self.preferred_format = opts.get('preferred_format')
        self.convertor = FFmpegVideoConvertorPP(opts.get('out_path'),
                                                preferedformat=self.preferred_format)
        self.convertor._deletetempfiles = opts.get('delete_tmp')
        self.convertor._downloader = DummyDownloader()
        self.file_path = opts.get('file_path')
        self.local_rowcount = opts.get('row_count')
        self.speed = '-- KiB/s'
        self.bytes = self.format_bytes(os.path.getsize(self.file_path))
        self.eta = "00:00"
        self.ext = self.file_path.split('.')[-1]
        # Signals
        self.signals = PostProcessorSignals()

    def convert(self):
        result = self.convertor.run({
            "ext": self.ext,
            "filepath": str(self.file_path),
        })
        return result

    def run(self):
        self.signals.list_Signal.emit([
            self.local_rowcount,
            os.path.split(self.file_path)[-1].split('.')[0],
            self.bytes,
            self.eta,
            self.speed,
            'Converting...'
        ])
        self.signals.statusBar_Signal.emit('Converting...')
        self.convert()
        self.signals.list_Signal.emit([
            self.local_rowcount,
            os.path.split(self.file_path)[-1].split('.')[0],
            self.bytes,
            self.eta,
            self.speed,
            'Finished'
        ])
        self.signals.statusBar_Signal.emit('Done!')

    def format_bytes(self, bytes):
        if bytes is None:
            return 'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'][exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return '%.2f%s' % (converted, suffix)