__author__ = 'yasoob'
from youtube_dl.postprocessor.ffmpeg import FFmpegVideoConvertorPP
from PyQt4 import QtCore

class PostProcessor(QtCore.QThread):
    """
    preffered_format
    filepath
    ext
    format
    """
    def __init__(self, file_path, preferred_format, parent=None):
        super(PostProcessor, self).__init__(parent)
        self.preferred_format = preferred_format
        self.convertor = FFmpegVideoConvertorPP(preferedformat=self.preferred_format)
        self.file_path = file_path

    def __del__(self):
        self.wait()

    def convert(self):
        result = self.convertor.run({
            "filepath": self.file_path,
            "ext": self.file_path.split('.')[-1],
        })
        return result

    def run(self):
        result = self.convert()
        return True