from UI.gui import Ui_MainWindow
from UI.batch_add_ui import Ui_BatchAdd
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import os
import time 
from download_thread import Download
from post_processor_thread import PostProcessor


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
        self.batch_dialogue = BatchAddDialogue(self)
        self.ui.lineEdit_2.setText(os.getcwd())
        self.ui.statusbar.showMessage('Ready.')
        self.set_connections()
        
        self.url_list = []
        self.thread_pool = {}
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.rowcount = 0

        self.connect_menu_action()
        self.setWindowTitle('youtube-dl v0.3.3')
        self.show()

    def set_connections(self):
        self.ui.download_btn.clicked.connect(self.handleButton)
        self.ui.browse_btn.clicked.connect(self.set_destination)
        self.ui.BatchAdd.clicked.connect(self.batch_file)

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
        self.ui.lineEdit_2.setText(file_name)

    def convert_file(self,file_path, preferred_format, delete_tmp=False):
        pass

    def download_url(self, url):
        directory = str(self.ui.lineEdit_2.text())
        quality = 'best'
        if self.ui.ConvertCheckBox.isChecked():
            quality = str(self.ui.ConvertComboBox.currentText())
        options = {
            'url': url,
            'directory': directory,
            'rowcount': self.rowcount,
            'proxy': '',
            'convert_format': quality,
            'parent':self,
        }
        if not self.ui.DeleteFileCheckBox.isChecked():
            options['keep_file'] = True

        self.thread_pool['thread{}'.format(self.rowcount)] = Download(options)

        self.thread_pool['thread{}'.format(self.rowcount)].statusSignal.connect(self.ui.statusbar.showMessage)
        self.thread_pool['thread{}'.format(self.rowcount)].remove_url_Signal.connect(self.remove_url)
        self.thread_pool['thread{}'.format(self.rowcount)].list_Signal.connect(self.add_to_table)
        self.thread_pool['thread{}'.format(self.rowcount)].row_Signal.connect(self.decrease_rowcount)
        self.thread_pool['thread{}'.format(self.rowcount)].start()

        self.ui.statusbar.showMessage('Extracting information..')
        self.rowcount += 1

        self.ui.tableWidget.setRowCount(self.rowcount)
        for m, key in enumerate([url, '', '', '', 'starting']):
            new_item = QtGui.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(0, m, new_item)

        self.url_list.append(url)
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
        if url not in self.url_list:
            self.download_url(url)
        else:
            self.ui.statusbar.showMessage('This url is already being downloaded')
            time.sleep(5)
            if len(self.url_list) is not 0:
                if len(self.url_list) < 2:
                    self.ui.statusbar.showMessage('Downloading {0} file'.format(len(self.url_list)))
                else:
                    self.ui.statusbar.showMessage('Downloading {0} files'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage("done")
    
    def remove_url(self,url):
        self.url_list.remove(url)

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
                value.exit()
            else:
                continue
        self.close()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
