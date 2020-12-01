import sys
import os


app_root = None

if not hasattr(sys, 'frozen'):
    # for import youtube_dl
    app_root = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
    sys.path.insert(0, app_root)
    

import youtube_dl
from PyQt5 import QtCore, QtGui, QtWidgets

from UI.gui import Ui_MainWindow
from GUI.BatchAddUrls import BatchAddDialogue
from GUI.LicenseDialog import LicenseDialogue
from GUI.AboutDialog import AboutDialog
from Threads.Download import Download
from Threads.PostProcessor import PostProcessor


# Setting custom variables
desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # For getting the icon to work
        try:
            from PyQt5.QtWinExtras import QtWin
            myappid = 'my_company.my_product.sub_product.version'
            QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
        except ImportError:
            pass
        
        global app_root
        if app_root:
            ico_path = os.path.join(app_root, 'UI', 'images', 'icon.ico')
        else:
            app_root = "."
            ico_path = ':/icon.ico'
        self.setWindowIcon(QtGui.QIcon(ico_path))
        self.batch_dialog = BatchAddDialogue(self)
        self.ui.saveToLineEdit.setText(desktop_path)
        self.ui.BrowseConvertToLineEdit.setText(os.getcwd())
        self.ui.BrowseConvertLineEdit.files = []
        self.ui.statusbar.showMessage('Ready.')
        self.set_connections()

        self.url_list = []
        self.complete_url_list = {}
        self.convert_list = []
        self.threadpool = QtCore.QThreadPool()
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.rowcount = 0

        self.connect_menu_action()

        self.about = AboutDialog(self)
        self.license = LicenseDialogue(self)
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
            urls = list(self.batch_dialog.ui.UrlList.toPlainText().split('\n'))
            for url in urls:
                if url.strip():
                    self.download_url(str(url))
        else:
            return

    def set_destination(self):
        file_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file_name:
            self.ui.saveToLineEdit.setText(file_name)

    def browse_convert_destination(self):
        file_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file_name:
            self.ui.BrowseConvertToLineEdit.setText(file_name)

    def convert_button(self):
        preferred_format = str(self.ui.ConvertMultipleComboBox.currentText())
        out_path = str(self.ui.BrowseConvertToLineEdit.text())
        delete_temp = self.ui.DeleteFileCheckBox.isChecked()
        if len(self.ui.BrowseConvertLineEdit.files) < 1:
            QtWidgets.QMessageBox.information(self, "Error!","No files given!")
            return

        for file_path in self.ui.BrowseConvertLineEdit.files:
            self.convert_file(file_path, out_path, preferred_format, delete_temp)

    def convert_file_browse(self):
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                               "Select files",
                                                               filter='Videos (*.mp4 *.ogg *.webm *.flv *.mkv)')
        if len(file_names) > 1:
            self.ui.BrowseConvertLineEdit.setText('{} Files selected'.format(len(file_names)))
            self.ui.BrowseConvertLineEdit.files=file_names
        elif len(file_names) == 1:
            self.ui.BrowseConvertLineEdit.setText(file_names[0])
            self.ui.BrowseConvertLineEdit.files=file_names
        else:
            self.ui.BrowseConvertLineEdit.files=file_names

    # TODO: Fix it
    def convert_file(self,file_path, out_path, preferred_format, delete_tmp=False):
        if file_path.split('.')[-1] == preferred_format:
            self.ui.statusbar.showMessage('The source and destination formats are same')
            return
        
        # TODO: Check file_path (file_name to final preferred_format)
        if file_path not in self.convert_list:
            options= {
                'file_path': file_path,
                'preferred_format': preferred_format,
                'row_count': self.rowcount,
                'delete_tmp': delete_tmp,
                'parent': self,
                'out_path': out_path,
            }
            # Using ThreadPool
            pprocessorThread = PostProcessor(options)
            pprocessorThread.signals.statusSignal.connect(self.ui.statusbar.showMessage)
            pprocessorThread.signals.list_Signal.connect(self.add_to_table)
            pprocessorThread.signals.row_Signal.connect(self.decrease_rowcount)
            self.threadpool.start(pprocessorThread)

            self.ui.tabWidget.setCurrentIndex(2)

            self.convert_list.append(file_path)
            self.add_to_table([
                self.rowcount,
                os.path.split(file_path)[-1].split('.')[0],
                '',
                '00:00',
                '-- KiB/s',
                'Converting'
            ])
            self.rowcount += 1

        else:
            self.ui.statusbar.showMessage('Already Converted')

    def download_url(self, url, row = None):
        if row is None:
            row = self.rowcount
        else:
            row = row

        directory = str(self.ui.saveToLineEdit.text())
        quality = False
        if self.ui.ConvertCheckBox.isChecked():
            quality = str(self.ui.ConvertComboBox.currentText())

        options = {
            'url': url,
            'directory': directory,
            'rowcount': row,
            'proxy': '',
            'convert_format': quality,
            'parent':self,
        }

        if not self.ui.DeleteFileCheckBox.isChecked():
            options['keep_file'] = True

        # Using ThreadPool
        downloadThread = Download(options)
        downloadThread.signals.status_bar_signal.connect(self.ui.statusbar.showMessage)
        downloadThread.signals.remove_url_signal.connect(self.remove_url)
        downloadThread.signals.add_update_list_signal.connect(self.add_to_table)
        downloadThread.signals.remove_row_signal.connect(self.decrease_rowcount)
        self.threadpool.start(downloadThread)

        self.ui.tabWidget.setCurrentIndex(2)
        self.ui.statusbar.showMessage('Extracting information...')

        self.url_list.append(url)
        self.complete_url_list[row] = url

        self.rowcount += 1

        if len(self.url_list):
            if len(self.url_list) < 2:
                self.ui.statusbar.showMessage('Downloading {0} file'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage('Downloading {0} files'.format(len(self.url_list)))
        else:
            self.ui.statusbar.showMessage("Done!")

    def handleButton(self):
        url = str(self.ui.videoUrlLineEdit.text())
        if url == '':
            QtWidgets.QMessageBox.information(self, "Error!","No url given!")
            return
        can_download, rowcount = self.can_download(url)
        if can_download:
            self.download_url(url, rowcount)
        else:
            QtWidgets.QMessageBox.information(self, "Error!","This url is already being downloaded")
            if len(self.url_list) != 0:
                if len(self.url_list) < 2:
                    self.ui.statusbar.showMessage('Downloading {0} file'.format(len(self.url_list)))
                else:
                    self.ui.statusbar.showMessage('Downloading {0} files'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage("Done!")

    def can_download(self,url):
        if url not in self.url_list:
            for row, _url in self.complete_url_list.items():
                if url == _url:
                    return True, row
            return True, self.rowcount
        else:
            return False, self.rowcount

    def remove_url(self,url):
        try:
            self.url_list.remove(url)
        except:
            pass

    def add_to_table(self, values):
        self.ui.tableWidget.setRowCount(self.rowcount)
        row = values[0]
        m = 0
        for key in values[1:]:
            new_item = QtWidgets.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(row, m, new_item)
            m += 1

    def decrease_rowcount(self):
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
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.Cancel:
                event.ignore()
            else:
                self.kill_all_threads()
        else:
            self.kill_all_threads()

    def kill_all_threads(self):
        self.threadpool.waitForDone(1)
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
