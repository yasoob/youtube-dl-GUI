from UI.gui import Ui_MainWindow
from UI.batch_add_ui import Ui_BatchAdd
from UI.licenseDialog import Ui_Dialog
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import os
from download_thread import Download
from post_processor_thread import PostProcessor

import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

try:
    approot = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    approot = os.path.dirname(os.path.abspath(sys.argv[0]))

class LicenseDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LicenseDialogue, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.ExitButton.clicked.connect(self.close)

class BatchAddDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        super(BatchAddDialogue, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ui = Ui_BatchAdd()
        self.ui.setupUi(self)
        self.download = False
        self.ui.Browse.clicked.connect(self.browse_clicked)
        self.ui.Close.clicked.connect(self.close)
        self.ui.Add.clicked.connect(self.add_clicked)

    def browse_clicked(self):
        file_name = str(QtGui.QFileDialog.getOpenFileName(self, "Select txt file",filter=QtCore.QString('*.txt')))
        if file_name is '':
            return
        with open(file_name, 'rb') as file_data:
            for line in file_data.readlines():
                self.ui.UrlList.append(line.strip())

    def add_clicked(self):
        if str(self.ui.UrlList.toPlainText()).strip() is '':
            QtGui.QMessageBox.information(self, "Error!","No urls given!")
            return
        else:
            self.download = True
            self.close()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        path = os.path.join(approot, 'UI', 'icon.png')
        self.setWindowIcon(QtGui.QIcon(path))
        self.batch_dialogue = BatchAddDialogue(self)
        self.ui.lineEdit_2.setText(os.getcwd())
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

    def batch_file(self):
        self.batch_dialogue.exec_()
        if self.batch_dialogue.download is True:
            urls = list(self.batch_dialogue.ui.UrlList.toPlainText().split('\n'))
            for url in urls:
                self.download_url(str(url))
        else:
            return

    def set_destination(self):
        file_name = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file_name is not '':
            self.ui.lineEdit_2.setText(file_name)

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
            self.convert_file(file_path, out_path, preferred_format,delete_temp)

    def convert_file_browse(self):
        file_names = [str(file_n) for file_n in list(QtGui.QFileDialog.getOpenFileNames(self, "Select files",
            filter=QtCore.QString('Videos (*.mp4 *.ogg *.webm *.flv *.mkv)')
        ))]
        if len(file_names) > 1:
            self.ui.BrowseConvertLineEdit.setText('{} Files selected'.format(len(file_names)))
            self.ui.BrowseConvertLineEdit.files = file_names
        elif len(file_names) == 1:
            self.ui.BrowseConvertLineEdit.setText(file_names[0])
            self.ui.BrowseConvertLineEdit.files = file_names
        else:
            self.ui.BrowseConvertLineEdit.files = file_names

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
            self.convert_list.append(file_path)
            self.ui.tabWidget.setCurrentIndex(2)
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
        if row >= 0:
            row = row
        elif row is None:
            row = self.rowcount

        directory = str(self.ui.lineEdit_2.text())
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
        self.thread_pool['thread{}'.format(row)].statusSignal.connect(self.ui.statusbar.showMessage)
        self.thread_pool['thread{}'.format(row)].remove_url_Signal.connect(self.remove_url)
        self.thread_pool['thread{}'.format(row)].list_Signal.connect(self.add_to_table)
        self.thread_pool['thread{}'.format(row)].row_Signal.connect(self.decrease_rowcount)
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
        url = str(self.ui.lineEdit.text())
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
        row = values[0]
        m = 0
        for key in values[1:]:
            new_item = QtGui.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(row, m, new_item)
            m += 1
        self.ui.tableWidget.setRowCount(self.rowcount)

    def decrease_rowcount(self):
        self.rowcount -= 1 

    def connect_menu_action(self):
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionLicense.triggered.connect(self.showLicense)

    def showLicense(self):
        license = LicenseDialogue(self)
        license.show()

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


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
