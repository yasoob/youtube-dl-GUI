from gui_code import Ui_Form
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys
import youtube_dl
import os

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # create stuff
        self.rw = MyForm()
        self.setCentralWidget(self.rw)
        self.createStatusBar()
        self.add_menu()

        # show windows
        self.setWindowTitle('youtube-dl v0.1')
        self.show()
        self.rw.show()

    def createStatusBar(self):
        sb = QtGui.QStatusBar()
        sb.setFixedHeight(18)
        self.setStatusBar(sb)

    def add_menu(self):
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)


class MyForm(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.img_label.setPixmap(QtGui.QPixmap(os.getcwd() + "/logo.png"))
        self.ui.pushButton.clicked.connect(self.handleButton)
        self.ui.lineEdit_2.setText(os.getcwd())
        self.ui.lineEdit_2.textEdited.connect(self.set_dest)

    def set_dest(self):
        file = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_2.setText(file)
    
    def handleButton(self):
        url = str(self.ui.lineEdit.text())
        if url is not '':
            self.download(url)
        else:
            self.ui.lineEdit.setPlaceholderText("No url given!")
        #self.ui.progressBar.setValue(19)

    def hook(self, li):
        self.ui.progressBar.setValue(int((float(li.get('downloaded_bytes')) / float(li.get('total_bytes')))*100.0))

    def download(self, url):
        directory = str(self.ui.lineEdit_2.text())
        ydl_options = {
            'outtmpl': '{0}/%(title)s-%(id)s.%(ext)s'.format(directory),
            'continuedl': True,
            'quiet' : True,
        }
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            ydl.add_default_info_extractors()
            ydl.add_progress_hook(self.hook)
            ydl.download([url])        
        self.ui.progressBar.setValue(0)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())

