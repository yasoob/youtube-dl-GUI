from PyQt5 import QtCore, QtWidgets
from UI.BatchAddUrls import Ui_BatchAdd


class BatchAddDialogue(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BatchAddDialogue, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ui = Ui_BatchAdd()
        self.ui.setupUi(self)
        self.download = False
        self.ui.Browse.clicked.connect(self.browse_clicked)
        self.ui.Close.clicked.connect(self.close_clicked)
        self.ui.Add.clicked.connect(self.add_clicked)

    def browse_clicked(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select txt file", filter='*.txt'
        )

        if file_name == '':
            return
        with open(file_name, 'r') as file_data:
            for line in file_data.readlines():
                self.ui.UrlList.append(line.strip())

    def add_clicked(self):
        if str(self.ui.UrlList.toPlainText()).strip() == '':
            QtWidgets.QMessageBox.information(self, "Error!", "No urls given!")
            return
        else:
            self.download = True
            self.close()
    
    def close_clicked(self):
        self.download = False
        self.close()
        