from gui import Ui_MainWindow
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import os
import time 
from download_thread import Download

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lineEdit_2.setText(os.getcwd())
        self.ui.statusbar.showMessage('Ready.')
        self.set_connections()
        
        self.url_list = []
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.rowcount = 0

        self.connect_menu_action()
        self.setWindowTitle('youtube-dl v0.3.0')
        self.show()

    def set_connections(self):
        self.ui.download_btn.clicked.connect(self.handleButton)
        self.ui.browse_btn.clicked.connect(self.set_dest)
        #self.ui.batch_btn.clicked.connect(self.batch_file)

    def batch_file(self):
        file = str(QtGui.QFileDialog.getOpenFileName(self, "Select txt file",filter = QtCore.QString('*.txt')))
        self.ui.lineEdit.setText(file)

    def set_dest(self):
        file = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_2.setText(file)
    
    def handleButton(self):
        url = str(self.ui.lineEdit.text())
        if url is '':
            QtGui.QMessageBox.information(self,"Error!","No url given!")
            return
        if url not in self.url_list:
            directory = str(self.ui.lineEdit_2.text())
            self.down_thread = Download(url,directory,self.rowcount)
            self.down_thread.statusSignal.connect(self.ui.statusbar.showMessage)
            self.down_thread.remove_url_Signal.connect(self.remove_url)
            self.down_thread.list_Signal.connect(self.add_to_table)
            self.down_thread.row_Signal.connect(self.increase_rowcount)
            self.down_thread.start()
            self.ui.statusbar.showMessage('Extracting information..')
            self.rowcount += 1
            self.url_list.append(url)
            if len(self.url_list) is not 0:
                if len(self.url_list) < 2:
                    self.ui.statusbar.showMessage('Downloading {0} song'.format(len(self.url_list)))
                else:
                    self.ui.statusbar.showMessage('Downloading {0} songs'.format(len(self.url_list)))
            else:
                self.ui.statusbar.showMessage("done")
        else:
            self.ui.statusbar.showMessage('This url is already being downloaded')
            time.sleep(5)
            if len(self.url_list) is not 0:
                if len(self.url_list) < 2:
                    self.ui.statusbar.showMessage('Downloading {0} song'.format(len(self.url_list)))
                else:
                    self.ui.statusbar.showMessage('Downloading {0} songs'.format(len(self.url_list)))
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

    def increase_rowcount(self):
        self.rowcount -= 1 

    def connect_menu_action(self):
        self.ui.actionExit.triggered.connect(QtGui.qApp.quit)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
