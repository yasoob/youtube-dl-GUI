__author__ = 'Yasoob'
from youtube_dl.postprocessor.ffmpeg import FFmpegVideoConvertorPP
from PyQt4 import QtCore


class PostProcessor(QtCore.QThread):
    """
    preferred_format
    filepath
    ext
    format
    """
    statusSignal = QtCore.pyqtSignal(QtCore.QString)
    remove_url_Signal = QtCore.pyqtSignal(str)
    list_Signal = QtCore.pyqtSignal([list])
    row_Signal = QtCore.pyqtSignal()
    error_occurred = False
    done = False

    def __init__(self, file_path, preferred_format, row_count, delete_tmp=False, parent=None):
        super(PostProcessor, self).__init__(parent)
        self.preferred_format = preferred_format
        self.convertor = FFmpegVideoConvertorPP(preferedformat=self.preferred_format)
        self.convertor._deletetempfiles = delete_tmp
        self.file_path = file_path
        self.local_rowcount = row_count

    def __del__(self):
        self.wait()

    def convert(self):
        try:
            result = self.convertor.run({
                "filepath": self.file_path,
                "ext": self.file_path.split('.')[-1],
            })
            return result
        except:
            self.row_Signal.emit()
            self.remove_url_Signal.emit(self.url)
            self.error_occurred = True
            self.statusSignal.emit(str("An Error Occurred"))
            return

    def run(self):
        self.convert()
        return True