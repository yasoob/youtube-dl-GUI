from UI.gui import Ui_MainWindow
from UI.batch_add_ui import Ui_BatchAdd
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import os
import time 
from download_thread import Download


class BatchAddDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        super(BatchAddDialogue, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ui = Ui_BatchAdd()
        self.ui.setupUi(self)
        self.download = False
        self.ui.Browse.clicked.connect(self.browse_clicked)
        self.ui.Close.clicked.connect(self.close)
        self.ui.Add.clicked.connect(self.addClicked)

    def browse_clicked(self):
        file = str(QtGui.QFileDialog.getOpenFileName(self, "Select txt file",filter = QtCore.QString('*.txt')))
        if file is '':
            return
        with open(file, 'rb') as file_data:
            for line in file_data.readlines():
                self.ui.UrlList.append(line.strip())

    def addClicked(self):
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
        self.thread_pool = []
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSortingEnabled(False)
        self.rowcount = 0

        self.connect_menu_action()
        self.setWindowTitle('youtube-dl v0.3.2')
        self.show()

    def set_connections(self):
        self.ui.download_btn.clicked.connect(self.handleButton)
        self.ui.browse_btn.clicked.connect(self.set_dest)
        self.ui.BatchAdd.clicked.connect(self.batch_file)

    def batch_file(self):
        self.batch_dialogue.exec_()
        if self.batch_dialogue.download is True:
            urls = list(self.batch_dialogue.ui.UrlList.toPlainText().split('\n'))
            for url in urls:
                self.download_url(str(url))
        else:
            return

    def set_dest(self):
        file = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_2.setText(file)

    def download_url(self, url):
        directory = str(self.ui.lineEdit_2.text())

        self.down_thread = Download(url, directory, self.rowcount, None, self)
        self.down_thread.statusSignal.connect(self.ui.statusbar.showMessage)
        self.down_thread.remove_url_Signal.connect(self.remove_url)
        self.down_thread.list_Signal.connect(self.add_to_table)
        self.down_thread.row_Signal.connect(self.decrease_rowcount)
        self.down_thread.start()
        self.ui.statusbar.showMessage('Extracting information..')

        self.rowcount += 1
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
        m=0
        for key in values[1:]:
            newitem = QtGui.QTableWidgetItem(key)
            self.ui.tableWidget.setItem(row, m, newitem)
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
                self.close()
        else:
            self.close()
        """
            exit_diag = QtGui.QMessageBox(self)
            exit_diag.setText("The document has been modified.")
            exit_diag.setInformativeText("Do you want to save your changes?")
            exit_diag.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Close)
            exit_diag.setDefaultButton(QtGui.QMessageBox)
            if exit_diag.exec_() == QtGui.QMessageBox.Close:
                self.close()
            else:
                event.ignore()
        """


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
