# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_add.ui'
#
# Created: Wed Jan 14 17:49:14 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_BatchAdd(object):
    def setupUi(self, BatchAdd):
        BatchAdd.setObjectName(_fromUtf8("BatchAdd"))
        BatchAdd.setWindowModality(QtCore.Qt.NonModal)
        BatchAdd.resize(400, 300)
        BatchAdd.setMaximumSize(QtCore.QSize(400, 16777215))
        BatchAdd.setModal(False)
        self.verticalLayout_2 = QtGui.QVBoxLayout(BatchAdd)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalWidget = QtGui.QWidget(BatchAdd)
        self.verticalWidget.setObjectName(_fromUtf8("verticalWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.UrlList = QtGui.QTextEdit(self.verticalWidget)
        self.UrlList.setObjectName(_fromUtf8("UrlList"))
        self.verticalLayout.addWidget(self.UrlList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.Browse = QtGui.QPushButton(self.verticalWidget)
        self.Browse.setObjectName(_fromUtf8("Browse"))
        self.horizontalLayout.addWidget(self.Browse)
        self.Add = QtGui.QPushButton(self.verticalWidget)
        self.Add.setObjectName(_fromUtf8("Add"))
        self.horizontalLayout.addWidget(self.Add)
        self.Close = QtGui.QPushButton(self.verticalWidget)
        self.Close.setObjectName(_fromUtf8("Close"))
        self.horizontalLayout.addWidget(self.Close)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.verticalWidget)

        self.retranslateUi(BatchAdd)
        QtCore.QMetaObject.connectSlotsByName(BatchAdd)

    def retranslateUi(self, BatchAdd):
        BatchAdd.setWindowTitle(_translate("BatchAdd", "Batch Add", None))
        self.Browse.setText(_translate("BatchAdd", "Browse", None))
        self.Add.setText(_translate("BatchAdd", "Add", None))
        self.Close.setText(_translate("BatchAdd", "Close", None))

