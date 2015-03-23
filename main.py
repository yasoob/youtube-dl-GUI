import sys
import os
from PyQt4 import QtGui
from PyQt4 import QtCore
import subprocess
from UI.gui import Ui_MainWindow
from GUI.BatchAddUrls import BatchAddDialogue
from GUI.LicenseDialog import LicenseDialogue
from GUI.AboutDialog import AboutDialog
from Threads.Download import Download
from Threads.PostProcessor import PostProcessor


# For getting the icon to work
import ctypes

ctypes.\
    windll.\
    shell32.\
    SetCurrentProcessExplicitAppUserModelID(
        'my_company.my_product.sub_product.version'
)

# Setting custom variables
desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
try:
    app_root = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    app_root = os.path.dirname(os.path.abspath(sys.argv[0]))


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path = os.path.join(app_root, 'UI', 'images', 'icon.png')
        self.setWindowIcon(QtGui.QIcon(path))
        self.batch_dialog = BatchAddDialogue(self)
        self.ui.saveToLineEdit.setText(desktop_path)
        self.ui.BrowseConvertToLineEdit.setText(os.getcwd())
        self.ui.BrowseConvertLineEdit.files = []
        self.ui.statusbar.showMessage('Ready.')
        self.set_connections()
        
        self.url_list = []
        self.complete_url_list = {}
        self.convert_list = []
        self.thread_pool = {}
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.rowcount = 0

        self.connect_menu_action()
        self.show()

    def set_connections(self):
        self.ui.download_btn.clicked.connect(self.handleButton)
        self.ui.browse_btn.clicked.connect(self.set_destination)
        self.ui.BatchAdd.clicked.connect(self.batch_file)
        self.ui.BrowseConvertButton.clicked.connect(self.convert_file_browse)
        self.ui.ConvertMultipleButton.clicked.connect(self.convert_button)
        self.ui.BrowseConvertToButton.clicked.connect(self.browse_convert_destination)
        self.ui.tableWidget.itemDoubleClicked.connect(self.open_file)

    def batch_file(self):
        self.batch_dialog.exec_()
        if self.batch_dialog.download is True:
            urls = list(self.batch_dialog.ui.UrlList.toPlainText().split('\n'))
            for url in urls:
                self.download_url(str(url))
        else:
            return

    def set_destination(self):
        file_name = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file_name is not '':
            self.ui.saveToLineEdit.setText(file_name)

    def browse_convert_destination(self):
        file_name = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file_name is not '':
            self.ui.BrowseConvertToLineEdit.setText(file_name)

    def convert_button(self):
        preferred_format = str(self.ui.ConvertMultipleComboBox.currentText())
        out_path = str(self.ui.BrowseConvertToLineEdit.text())
        delete_temp = self.ui.DeleteFileCheckBox.isChecked()
        if len(self.ui.BrowseConvertLineEdit.files) < 1:
            QtGui.QMessageBox.information(self, "Error!","No files given!")
            return

        for file_path in self.ui.BrowseConvertLineEdit.files:
            self.convert_file(file_path, out_path, preferred_format, delete_temp)

    def convert_file_browse(self):
        file_names = [str(file_n) for file_n in list(
            QtGui.QFileDialog.getOpenFileNames(self, "Select files",
                filter=QtCore.QString('Videos (*.mp4 *.ogg *.webm *.flv *.mkv)')
            ))
        ]
        if len(file_names) > 1:
            self.ui.BrowseConvertLineEdit.setText('{} Files selected'.format(len(file_names)))
            self.ui.BrowseConvertLineEdit.files=file_names
        elif len(file_names) == 1:
            self.ui.BrowseConvertLineEdit.setText(file_names[0])
            self.ui.BrowseConvertLineEdit.files=file_names
        else:
            self.ui.BrowseConvertLineEdit.files=file_names

    def convert_file(self,file_path, out_path, preferred_format, delete_tmp=False):
        if file_path.split('.')[-1] == preferred_format:
            self.ui.statusbar.showMessage('The source and destination formats are same')
            return

        if file_path not in self.convert_list:
            options= {
                'file_path': file_path,
                'preferred_format': preferred_format,
                'row_count': self.rowcount,
                'delete_tmp': delete_tmp,
                'parent': self,
                'out_path': out_path,
            }
            self.thread_pool['thread{}'.format(self.rowcount)] = PostProcessor(options)
            self.thread_pool['thread{}'.format(self.rowcount)].statusSignal.connect(self.ui.statusbar.showMessage)
            self.thread_pool['thread{}'.format(self.rowcount)].list_Signal.connect(self.add_to_table)
            self.thread_pool['thread{}'.format(self.rowcount)].row_Signal.connect(self.decrease_rowcount)
            self.thread_pool['thread{}'.format(self.rowcount)].start()
            self.ui.tabWidget.setCurrentIndex(2)

            self.convert_list.append(file_path)

            self.add_to_table([
                self.rowcount,
                os.path.split(file_path)[-1].split('.')[0],
                '',
                '00:00',
                '-- KiB/s',
                'Converting',
                file_path
            ])
            self.rowcount += 1

        else:
            self.ui.statusbar.showMessage('Already Converted')

    def download_url(self, url, row = None):
        if row >= 0:
            row = row
        elif row is None:
            row = self.rowcount

        directory = str(self.ui.saveToLineEdit.text())
        quality = False
        if self.ui.ConvertCheckBox.isChecked():
            quality = str(self.ui.ConvertComboBox.currentText())
        print row, self.rowcount
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

        self.thread_pool['thread{}'.format(row)] = Download(options)
        self.thread_pool['thread{}'.format(row)].status_bar_signal.connect(self.ui.statusbar.showMessage)
        self.thread_pool['thread{}'.format(row)].remove_url_signal.connect(self.remove_url)
        self.thread_pool['thread{}'.format(row)].add_update_list_signal.connect(self.add_to_table)
        self.thread_pool['thread{}'.format(row)].remove_row_signal.connect(self.decrease_rowcount)
        self.thread_pool['thread{}'.format(row)].start()

        self.ui.tabWidget.setCurrentIndex(2)
        self.ui.statusbar.showMessage('Extracting information..')

        self.url_list.append(url)
        self.complete_url_list[row] = url

        self.rowcount += 1

        if len(self.url_list) is not 0:
            if len(self.url_list) < 2:
                self.ui.statusbar.showMessage('Downloading {0} file'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage('Downloading {0} files'.format(len(self.url_list)))
        else:
            self.ui.statusbar.showMessage("done")

    def handleButton(self):
        url = str(self.ui.videoUrlLineEdit.text())
        if url is '':
            QtGui.QMessageBox.information(self, "Error!","No url given!")
            return
        can_download, rowcount = self.can_download(url)
        if can_download:
            self.download_url(url, rowcount)
        else:
            QtGui.QMessageBox.information(self, "Error!","This url is already being downloaded")
            if len(self.url_list) is not 0:
                if len(self.url_list) < 2:
                    self.ui.statusbar.showMessage('Downloading {0} file'.format(len(self.url_list)))
                else:
                    self.ui.statusbar.showMessage('Downloading {0} files'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage("done")

    def can_download(self,url):
        if url not in self.url_list:
            for row, _url in self.complete_url_list.iteritems():
                if url == _url:
                    print "url already there:"
                    print row, self.rowcount
                    return True, row
            print "url not already there:"
            print self.rowcount, self.rowcount
            return True, self.rowcount
        else:
            return False, self.rowcount

    def remove_url(self,url):
        try:
            self.url_list.remove(url)
        except:
            print url
            print self.url_list
            return

    def add_to_table(self, values):
        self.ui.tableWidget.setRowCount(self.rowcount)
        row = values[0]
        m = 0
        for key in values[1:]:
            new_item = QtGui.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(row, m, new_item)
            m += 1

    def decrease_rowcount(self):
        self.rowcount -= 1 

    def connect_menu_action(self):
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionLicense.triggered.connect(self.showLicense)
        self.ui.actionAbout.triggered.connect(self.showAbout)

    def showLicense(self):
        license = LicenseDialogue(self)
        license.show()

    def showAbout(self):
        about = AboutDialog(self)
        about.show()

    def closeEvent(self, event):
        if len(self.url_list) is not 0:
            msgBox = QtGui.QMessageBox(self)
            msgBox.setWindowTitle("Exit")
            msgBox.setText("Some files are currently being downloaded.")
            msgBox.setInformativeText("Do you really want to close?")
            msgBox.setStandardButtons(QtGui.QMessageBox.Close | QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.Cancel:
                event.ignore()
            else:
                self.kill_all_threads()
        else:
            self.kill_all_threads()

    def kill_all_threads(self):
        for key, value in self.thread_pool.iteritems():
            if value.done is False:
                del value
            else:
                continue
        self.close()

    def open_file(self):
        row = self.ui.tableWidget.currentRow()
        file_name = str(self.ui.tableWidget.item(row,5).text().toUtf8())
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', file_name))
        elif os.name == 'nt':
            os.startfile(file_name)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', file_name))



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
