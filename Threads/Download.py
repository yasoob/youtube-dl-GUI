import math
from pathlib import Path

import youtube_dl
from PyQt5 import QtCore


class StopError(Exception):
    pass


class DownloadSignals(QtCore.QObject):
    "Define the signals available from a running download thread"

    status_bar_signal = QtCore.pyqtSignal(str)
    remove_url_signal = QtCore.pyqtSignal(str)
    add_update_list_signal = QtCore.pyqtSignal([list])
    remove_row_signal = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()


class Download(QtCore.QRunnable):
    "Download Thread"

    def __init__(self, opts):
        super(Download, self).__init__()
        self.parent = opts.get("parent")
        self.error_occurred = False
        self.done = False
        self.file_name = ""
        self.speed = "-- KiB/s"
        self.eta = "00:00"
        self.bytes = self.format_bytes(None)
        self.url = opts.get("url")
        self.directory = opts.get("directory")
        if self.directory:
            self.directory = str(Path(opts.get("directory")).resolve())
        self.local_rowcount = opts.get("rowcount")
        self.convert_format = opts.get("convert_format")
        self.proxy = opts.get("proxy")
        self.keep_file = opts.get("keep_file")
        # Signals
        self.signals = DownloadSignals()

    def hook(self, li):
        if self.done:
            raise StopError()
        
        _file_name = li.get("filename")

        if li.get("downloaded_bytes"):
            if li.get("speed"):
                self.speed = self.format_speed(li.get("speed"))
                self.eta = self.format_seconds(li.get("eta"))
                self.bytes = self.format_bytes(li.get("total_bytes", "unknown"))
                filename = str(Path(_file_name).stem)
                self.signals.add_update_list_signal.emit(
                    [
                        self.local_rowcount,
                        filename,
                        self.bytes,
                        self.eta,
                        self.speed,
                        li.get("status"),
                    ]
                )  

            elif li.get("status") == "finished":
                self.file_name = str(Path(_file_name).stem)
                self.signals.add_update_list_signal.emit(
                    [
                        self.local_rowcount,
                        self.file_name,
                        self.bytes,
                        self.eta,
                        self.speed,
                        "Converting",
                    ]
                )  
        else:
            self.bytes = self.format_bytes(li.get("total_bytes"))
            self.file_name = Path(_file_name).name
            self.speed = "-- KiB/s"

            self.signals.add_update_list_signal.emit(
                [
                    self.local_rowcount,
                    self.file_name,
                    self.bytes,
                    "00:00",
                    self.speed,
                    "Finished",
                ]
            )  
            self.signals.status_bar_signal.emit("Already Downloaded")  
            self.signals.remove_row_signal.emit()  

    def _prepare_ytd_options(self):
        ydl_options = {
            "outtmpl": f"{self.directory}/%(title)s-%(id)s.%(ext)s",
            "continuedl": True,
            "quiet": True,
            "proxy": self.proxy,
        }
        if self.convert_format is not False:
            ydl_options["postprocessors"] = [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": self.convert_format,
                }
            ]

        if self.keep_file:
            ydl_options["keepvideo"] = True
        return ydl_options

    def download(self):
        ydl_options = self._prepare_ytd_options()
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.add_default_info_extractors()
            ydl.add_progress_hook(self.hook)
            try:
                ydl.download([self.url])
            except (
                youtube_dl.utils.DownloadError,
                youtube_dl.utils.ContentTooShortError,
                youtube_dl.utils.ExtractorError,
                youtube_dl.utils.UnavailableVideoError,
            ) as e:
                self.error_occurred = True
                self.signals.remove_row_signal.emit()  
                self.signals.remove_url_signal.emit(self.url)  
                self.signals.status_bar_signal.emit(str(e))  
            except StopError:
                # import threading
                # print("Exiting thread:", threading.currentThread().getName())
                self.done = True
                self.signals.finished.emit()  

    @QtCore.pyqtSlot()
    def run(self):
        self.signals.add_update_list_signal.emit(
            [self.local_rowcount, self.url, "", "", "", "Starting"]
        )  

        self.download()

        if self.error_occurred is not True:
            self.signals.add_update_list_signal.emit(
                [
                    self.local_rowcount,
                    self.file_name,
                    self.bytes,
                    "00:00",
                    self.speed,
                    "Finished",
                ]
            )  

            self.signals.status_bar_signal.emit("Done!")  
        self.signals.remove_url_signal.emit(self.url)  
        self.done = True
        self.signals.finished.emit()  

    def stop(self):
        self.done = True

    def format_seconds(self, seconds):
        (minutes, secs) = divmod(seconds, 60)
        (hours, minutes) = divmod(minutes, 60)
        if hours > 99:
            return "--:--:--"
        if hours == 0:
            return "%02d:%02d" % (minutes, secs)
        else:
            return "%02d:%02d:%02d" % (hours, minutes, secs)

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

    def format_speed(self, speed=None):
        if not speed:
            return "%10s" % "---b/s"
        return "%10s" % ("%s/s" % self.format_bytes(speed))
