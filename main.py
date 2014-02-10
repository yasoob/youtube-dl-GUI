from gui import Ui_MainWindow
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import youtube_dl
import os
import time 
import math

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label.setPixmap(QtGui.QPixmap(os.getcwd() + "/logo.png"))
        self.ui.lineEdit_2.setText(os.getcwd())
        self.ui.statusbar.showMessage('Ready.')
        self.set_connections()
        
        self.ui.tableWidget.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.ui.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.rowcount = 0

        self.connect_menu_action()
        self.setWindowTitle('youtube-dl v0.1')
        self.show()

    def set_connections(self):
        self.ui.pushButton.clicked.connect(self.handleButton)
        self.ui.lineEdit_2.textEdited.connect(self.set_dest)

    def set_dest(self):
        file = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_2.setText(file)
    
    def handleButton(self):
        url = str(self.ui.lineEdit.text())
        if url is '':
            QtGui.QMessageBox.information(self,"Error!","No url given!")
            return
        directory = str(self.ui.lineEdit_2.text())
        self.down_thread = Download(url,directory,self.rowcount)
        self.down_thread.statusSignal.connect(self.ui.statusbar.showMessage)
        self.down_thread.p_barSignal.connect(self.ui.progressBar.setValue)
        self.down_thread.list_Signal.connect(self.add_to_table)
        self.down_thread.row_Signal.connect(self.increase_rowcount)
        self.down_thread.start()
        self.rowcount += 1

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
        
class Download(QtCore.QThread):
    statusSignal = QtCore.pyqtSignal(QtCore.QString)
    p_barSignal = QtCore.pyqtSignal(int)
    list_Signal = QtCore.pyqtSignal([list])
    row_Signal = QtCore.pyqtSignal()

    def __init__(self,url,directory,rowcount):
        super(Download,self).__init__()
        self.url = url
        self.directory = directory
        self.local_rowcount = rowcount
        if self.directory is not '':
            self.directory = directory + '/'

    def hook(self, li):
        if li.get('downloaded_bytes') is not None:
            self.p_barSignal.emit(int((float(li.get('downloaded_bytes')) / float(li.get('total_bytes')))*100.0))
            if li.get('speed') is not None:
                self.speed = self.format_speed(li.get('speed'))
                self.eta = self.format_seconds(li.get('eta'))
                self.list_Signal.emit( [self.local_rowcount, li.get('filename').split('/')[-1],self.eta,self.speed,li.get('status')])
            elif li.get('status') == "finished":
                self.list_Signal.emit( [self.local_rowcount, li.get('filename').split('/')[-1],self.eta,self.speed,li.get('status')])
        else:
            self.statusSignal.emit('Already Downloaded')
            time.sleep(10)
            return
        if li.get('eta') is not None:
            filename = li.get('filename').split('/')[-1][:25]+'..'
            self.statusSignal.emit('Downloading '+filename+' - '+self.format_seconds(li.get('eta')))

    def download(self):
        ydl_options = {
            'outtmpl': '{0}%(title)s-%(id)s.%(ext)s'.format(self.directory),
            'continuedl': True,
            'quiet' : True,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.add_default_info_extractors()
            ydl.add_progress_hook(self.hook)
            try:
                ydl.download([self.url])        
            except (youtube_dl.utils.DownloadError,youtube_dl.utils.ContentTooShortError,youtube_dl.utils.ExtractorError) as e:
                self.row_Signal.emit()
                self.statusSignal.emit(str(e))
        self.p_barSignal.emit(0)

    def run(self):
        self.filenameSent = False
        self.statusSignal.emit('Extracting information..')
        self.download()
        #self.statusSignal.emit('Done!')

    def format_seconds(self,seconds):
        (mins, secs) = divmod(seconds, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            return '--:--:--'
        if hours == 0:
            return '%02d:%02d' % (mins, secs)
        else:
            return '%02d:%02d:%02d' % (hours, mins, secs)

    def format_bytes(self,bytes):
        if bytes is None:
            return u'N/A'
        if type(bytes) is str:
            bytes = float(bytes)
        if bytes == 0.0:
            exponent = 0
        else:
            exponent = int(math.log(bytes, 1024.0))
        suffix = [u'B', u'KiB', u'MiB', u'GiB', u'TiB', u'PiB', u'EiB', u'ZiB', u'YiB'][exponent]
        converted = float(bytes) / float(1024 ** exponent)
        return u'%.2f%s' % (converted, suffix)

    def format_speed(self,speed):
        if speed is None:
            return '%10s' % '---b/s'
        return '%10s' % ('%s/s' % self.format_bytes(speed))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

