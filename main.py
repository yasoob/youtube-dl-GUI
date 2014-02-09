from gui import Ui_MainWindow
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import youtube_dl
import os
import time 

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label.setPixmap(QtGui.QPixmap(os.getcwd() + "/logo.png"))
        self.ui.pushButton.clicked.connect(self.handleButton)
        self.ui.lineEdit_2.setText(os.getcwd())
        self.ui.lineEdit_2.textEdited.connect(self.set_dest)

        self.setWindowTitle('youtube-dl v0.1')
        self.show()


    def set_dest(self):
        file = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_2.setText(file)
    
    def handleButton(self):
        url = str(self.ui.lineEdit.text())
        if url is '':
            QtGui.QMessageBox.information(self,"Error!","No url given!")
        
        directory = str(self.ui.lineEdit_2.text())
        self.down_thread = Download(url,directory)
        self.down_thread.statusSignal.connect(self.ui.statusbar.showMessage)
        self.down_thread.p_barSignal.connect(self.change_progress)
        self.down_thread.start()

    def change_progress(self,e):
        self.ui.progressBar.setValue(int(e))

class Download(QtCore.QThread):
    statusSignal = QtCore.pyqtSignal(QtCore.QString)
    p_barSignal = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self,url,directory):
        super(Download,self).__init__()
        self.url = url
        self.directory = directory
        if self.directory is not '':
            self.directory = directory + '/'

    def hook(self, li):
        if li.get('downloaded_bytes') is not None:
            self.p_barSignal.emit(str(int((float(li.get('downloaded_bytes')) / float(li.get('total_bytes')))*100.0)))
        else:
            self.statusSignal.emit('Already Downloaded')
            time.sleep(10)
            return
        if li.get('eta') is not None:
            self.statusSignal.emit(self.format_seconds(li.get('eta')))

    def download(self):
        ydl_options = {
            'outtmpl': '{0}%(title)s-%(id)s.%(ext)s'.format(self.directory),
            'continuedl': True,
            'quiet' : True,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.add_default_info_extractors()
            ydl.add_progress_hook(self.hook)
            ydl.download([self.url])        
        self.p_barSignal.emit(str(0))

    def run(self):
        self.statusSignal.emit('Extracting information..')
        self.download()
        self.statusSignal.emit('Done!')

    def format_seconds(self,seconds):
        (mins, secs) = divmod(seconds, 60)
        (hours, mins) = divmod(mins, 60)
        if hours > 99:
            return '--:--:--'
        if hours == 0:
            return '%02d:%02d minutes left' % (mins, secs)
        else:
            return '%02d:%02d:%02d hours left' % (hours, mins, secs)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
