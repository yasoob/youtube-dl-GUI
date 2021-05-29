import math
from pathlib import Path

from PyQt5 import QtCore
from youtube_dl.postprocessor.ffmpeg import FFmpegPostProcessor


class FFmpegVideoConvertorPP(FFmpegPostProcessor):
    def __init__(self, outpath, downloader=None, preferedformat=""):
        super(FFmpegVideoConvertorPP, self).__init__(downloader)
        self._preferedformat = preferedformat
        self.outpath = outpath

    def run(self, information):
        _path = information["filepath"]
        file_name = Path(_path).name

        if information["ext"] == self._preferedformat:
            return True, information

        self.outpath = str(
            Path(self.outpath) / Path(file_name).with_suffix(f".{self._preferedformat}")
        )

        self.run_ffmpeg(_path, self.outpath, [])
        information["filepath"] = self.outpath
        information["format"] = self._preferedformat
        information["ext"] = self._preferedformat
        return False, information


class DummyDownloader:
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
        self.parent = opts.get("parent")
        self.error_occurred = False
        self.done = False
        self.preferred_format = opts.get("preferred_format")
        self.convertor = FFmpegVideoConvertorPP(
            opts.get("out_path"), preferedformat=self.preferred_format
        )
        self.convertor._deletetempfiles = opts.get("delete_tmp")  # type: ignore
        self.convertor._downloader = DummyDownloader()
        self.file_path: str = opts.get("file_path")
        self.local_rowcount = opts.get("row_count")
        self.speed = "-- KiB/s"
        self.bytes = self.format_bytes(Path(self.file_path).lstat().st_size)
        self.eta = "00:00"
        self.ext = Path(self.file_path).suffix
        # Signals
        self.signals = PostProcessorSignals()

    def convert(self):
        result = self.convertor.run(
            {
                "ext": self.ext,
                "filepath": self.file_path,
            }
        )
        return result

    def run(self):
        _file_path = Path(self.file_path).stem

        self.signals.list_Signal.emit(
            [
                self.local_rowcount,
                _file_path,
                self.bytes,
                self.eta,
                self.speed,
                "Converting...",
            ]
        )  # type: ignore
        self.signals.statusBar_Signal.emit("Converting...")  # type: ignore
        self.convert()
        self.signals.list_Signal.emit(
            [
                self.local_rowcount,
                _file_path,
                self.bytes,
                self.eta,
                self.speed,
                "Finished",
            ]
        )  # type: ignore
        self.signals.statusBar_Signal.emit("Done!")  # type: ignore

    # TODO: Move to utils
    def format_bytes(self, _bytes=None):
        if not _bytes:
            return "N/A"

        _bytes = float(_bytes)

        if _bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(_bytes, 1024.0))

        suffix = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"][exponent]
        converted = _bytes / float(1024 ** exponent)
        return "%.2f%s" % (converted, suffix)
