# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources\batch_add.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BatchAdd(object):
    def setupUi(self, BatchAdd):
        BatchAdd.setObjectName("BatchAdd")
        BatchAdd.setWindowModality(QtCore.Qt.NonModal)
        BatchAdd.resize(400, 300)
        BatchAdd.setMaximumSize(QtCore.QSize(400, 16777215))
        BatchAdd.setModal(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(BatchAdd)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalWidget = QtWidgets.QWidget(BatchAdd)
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.UrlList = QtWidgets.QTextEdit(self.verticalWidget)
        self.UrlList.setObjectName("UrlList")
        self.verticalLayout.addWidget(self.UrlList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Browse = QtWidgets.QPushButton(self.verticalWidget)
        self.Browse.setObjectName("Browse")
        self.horizontalLayout.addWidget(self.Browse)
        self.Add = QtWidgets.QPushButton(self.verticalWidget)
        self.Add.setObjectName("Add")
        self.horizontalLayout.addWidget(self.Add)
        self.Close = QtWidgets.QPushButton(self.verticalWidget)
        self.Close.setObjectName("Close")
        self.horizontalLayout.addWidget(self.Close)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.verticalWidget)

        self.retranslateUi(BatchAdd)
        QtCore.QMetaObject.connectSlotsByName(BatchAdd)

    def retranslateUi(self, BatchAdd):
        _translate = QtCore.QCoreApplication.translate
        BatchAdd.setWindowTitle(_translate("BatchAdd", "Batch Add"))
        self.Browse.setText(_translate("BatchAdd", "Browse"))
        self.Add.setText(_translate("BatchAdd", "Add"))
        self.Close.setText(_translate("BatchAdd", "Close"))
