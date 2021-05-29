# Entry point to the app
import os
import sys
from pathlib import Path

app_root = None

if not hasattr(sys, "frozen"):
    # direct call of __main__.py
    PATH = Path(__file__).resolve().parent
    app_root = str(PATH)
    sys.path.insert(0, app_root)


from PyQt5 import QtCore, QtGui, QtWidgets

import youtube_dl
from GUI.AboutDialog import AboutDialog
from GUI.BatchAddUrls import BatchAddDialogue
from GUI.LicenseDialog import LicenseDialogue
from Threads.Download import Download
from Threads.PostProcessor import PostProcessor
from UI.gui import Ui_MainWindow

# Setting custom variables
desktop_path = str(Path().home() / Path("Desktop"))

if not Path(desktop_path).exists():
    os.makedirs(desktop_path, exist_ok=True)


class CloseSignals(QtCore.QObject):
    "Define the signals available for close"

    closed = QtCore.pyqtSignal()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # For getting the icon to work
        try:
            from PyQt5.QtWinExtras import QtWin  # type: ignore

            myappid = "my_company.my_product.sub_product.version"
            QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
        except ImportError:
            pass

        global app_root
        if app_root:
            ico_path = str(Path(app_root) / Path("UI/images/icon.ico"))
        else:
            app_root = ":/"
            ico_path = app_root + "icon.ico"
        self.setWindowIcon(QtGui.QIcon(ico_path))
        self.batch_dialog = BatchAddDialogue(self)
        self.ui.saveToLineEdit.setText(desktop_path)
        self.ui.BrowseConvertToLineEdit.setText(str(Path().cwd()))
        self.ui.BrowseConvertLineEdit.files = []  # type: ignore
        self.ui.statusbar.showMessage("Ready.")
        self.set_connections()

        self.url_list = []
        self.complete_url_list = {}
        self.convert_list = []
        self.threadpool = QtCore.QThreadPool()
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.rowcount = 0

        self.connect_menu_action()

        self.about = AboutDialog(self)
        self.license = LicenseDialogue(self)
        self.closing = CloseSignals()
        self.show()

    def set_connections(self):
        self.ui.download_btn.clicked.connect(self.handleButton)
        self.ui.browse_btn.clicked.connect(self.set_destination)
        self.ui.BatchAdd.clicked.connect(self.batch_file)
        self.ui.BrowseConvertButton.clicked.connect(self.convert_file_browse)
        self.ui.ConvertMultipleButton.clicked.connect(self.convert_button)
        self.ui.BrowseConvertToButton.clicked.connect(self.browse_convert_destination)

    def batch_file(self):
        self.batch_dialog.exec_()

        if self.batch_dialog.download is True:
            urls = list(self.batch_dialog.ui.UrlList.toPlainText().split("\n"))
            for url in urls:
                if url.strip():
                    self.download_url(str(url))

    def set_destination(self):
        file_name: str = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory"
        )
        if file_name:
            self.ui.saveToLineEdit.setText(str(Path(file_name).resolve()))

    def browse_convert_destination(self):
        file_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if file_name:
            self.ui.BrowseConvertToLineEdit.setText(str(Path(file_name).resolve()))

    def convert_button(self):
        preferred_format = self.ui.ConvertMultipleComboBox.currentText()
        out_path = self.ui.BrowseConvertToLineEdit.text()
        delete_temp = self.ui.DeleteFileCheckBox.isChecked()

        if len(self.ui.BrowseConvertLineEdit.files) < 1:
            QtWidgets.QMessageBox.information(self, "Error!", "No files given!")
        else:
            for file_path in self.ui.BrowseConvertLineEdit.files:
                self.convert_file(file_path, out_path, preferred_format, delete_temp)

    def convert_file_browse(self):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select files", filter="Videos (*.mp4 *.ogg *.webm *.flv *.mkv)"
        )

        if len(file_names) > 1:
            self.ui.BrowseConvertLineEdit.setText(f"{len(file_names)} Files selected")
        elif len(file_names) == 1:
            file_name = str(Path(file_names[0]).resolve())
            self.ui.BrowseConvertLineEdit.setText(file_name)

        self.ui.BrowseConvertLineEdit.files = file_names  # type: ignore

    def convert_file(self, file_path, out_path, preferred_format, delete_tmp=False):
        if Path(file_path).suffix == preferred_format:
            self.ui.statusbar.showMessage("The source and destination formats are same")
            return

        if file_path not in self.convert_list:
            options = {
                "file_path": file_path,
                "preferred_format": preferred_format,
                "row_count": self.rowcount,
                "delete_tmp": delete_tmp,
                "parent": self,
                "out_path": out_path,
            }
            # Using ThreadPool
            pprocessorThread = PostProcessor(options)
            pprocessorThread.signals.statusBar_Signal.connect(self.ui.statusbar.showMessage)  # type: ignore
            pprocessorThread.signals.list_Signal.connect(self.add_to_table)  # type: ignore
            pprocessorThread.signals.row_Signal.connect(self.decrease_rowcount)  # type: ignore
            self.threadpool.start(pprocessorThread)

            self.ui.tabWidget.setCurrentIndex(2)

            self.convert_list.append(file_path)
            self.add_to_table(
                [
                    self.rowcount,
                    Path(file_path).stem,
                    "",
                    "00:00",
                    "-- KiB/s",
                    "Converting",
                ]
            )
            self.rowcount += 1
        else:
            self.ui.statusbar.showMessage("Already Converted")

    def download_url(self, url, row=None):
        if row is None:
            row = self.rowcount

        directory = str(Path(self.ui.saveToLineEdit.text()).resolve())
        quality = False
        if self.ui.ConvertCheckBox.isChecked():
            quality = self.ui.ConvertComboBox.currentText()

        options = {
            "url": url,
            "directory": directory,
            "rowcount": row,
            "proxy": "",
            "convert_format": quality,
            "parent": self,
        }

        if not self.ui.DeleteFileCheckBox.isChecked():
            options["keep_file"] = True

        # Using ThreadPool
        downloadThread = Download(options)
        downloadThread.signals.status_bar_signal.connect(self.ui.statusbar.showMessage)  # type: ignore
        downloadThread.signals.remove_url_signal.connect(self.remove_url)  # type: ignore
        downloadThread.signals.add_update_list_signal.connect(self.add_to_table)  # type: ignore
        downloadThread.signals.remove_row_signal.connect(self.decrease_rowcount)  # type: ignore
        self.closing.closed.connect(downloadThread.stop)  # type: ignore
        self.threadpool.start(downloadThread)

        self.ui.tabWidget.setCurrentIndex(2)
        self.ui.statusbar.showMessage("Extracting information...")

        self.url_list.append(url)
        self.complete_url_list[row] = url

        self.rowcount += 1

        if len(self.url_list):
            if len(self.url_list) == 1:
                self.ui.statusbar.showMessage("Downloading 1 file")
            else:
                self.ui.statusbar.showMessage(f"Downloading {len(self.url_list)} files")
        else:
            self.ui.statusbar.showMessage("Done!")

    def handleButton(self):
        url = self.ui.videoUrlLineEdit.text()

        if not url:
            QtWidgets.QMessageBox.information(self, "Error!", "No url given!")
            return

        can_download, rowcount = self.can_download(url)
        if can_download:
            self.download_url(url, rowcount)
        else:
            QtWidgets.QMessageBox.information(
                self, "Error!", "This url is already being downloaded"
            )
            if len(self.url_list):
                if len(self.url_list) == 1:
                    self.ui.statusbar.showMessage("Downloading 1 file")
                else:
                    self.ui.statusbar.showMessage(
                        f"Downloading {len(self.url_list)} files"
                    )
            else:
                self.ui.statusbar.showMessage("Done!")

    def can_download(self, url):
        if url not in self.url_list:
            for row, _url in self.complete_url_list.items():
                if url == _url:
                    return True, row
            return True, self.rowcount
        else:
            return False, self.rowcount

    def remove_url(self, url):
        # TODO: Need synchronized List/Queue
        try:
            self.url_list.remove(url)
        except:
            pass

    def add_to_table(self, values):
        self.ui.tableWidget.setRowCount(self.rowcount)
        row = values[0]
        column = 0
        for key in values[1:]:
            new_item = QtWidgets.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(row, column, new_item)
            column += 1

    def decrease_rowcount(self):
        # TODO: Check decrease >= 0
        self.rowcount -= 1

    def connect_menu_action(self):
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionLicense.triggered.connect(self.showLicense)
        self.ui.actionAbout.triggered.connect(self.showAbout)

    def showLicense(self):
        self.license.show()

    def showAbout(self):
        self.about.show()

    def closeEvent(self, event):
        if len(self.url_list):
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setWindowTitle("Exit")
            msgBox.setText("Some files are currently being downloaded.")
            msgBox.setInformativeText("Do you really want to close?")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)  # type: ignore
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.Cancel:
                event.ignore()
            else:
                self.kill_all_threads()
        else:
            self.kill_all_threads()

    def kill_all_threads(self):
        self.closing.closed.emit()  # type: ignore
        self.threadpool.waitForDone()
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    sys.exit(main())
