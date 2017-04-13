# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sweep_runner.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(581, 101)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 581, 101))
        self.horizontalLayoutWidget_2.setObjectName(_fromUtf8("horizontalLayoutWidget_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbl_steps_complete = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lbl_steps_complete.setReadOnly(True)
        self.lbl_steps_complete.setObjectName(_fromUtf8("lbl_steps_complete"))
        self.gridLayout.addWidget(self.lbl_steps_complete, 1, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit.setStyleSheet(_fromUtf8("QLineEdit { background-color: rgb(224,224,224) }"))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.lineEdit_3 = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit_3.setStyleSheet(_fromUtf8("QLineEdit { background-color: rgb(224,224,224) }"))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.gridLayout.addWidget(self.lineEdit_3, 0, 1, 1, 1)
        self.lbl_steps_total = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lbl_steps_total.setReadOnly(True)
        self.lbl_steps_total.setObjectName(_fromUtf8("lbl_steps_total"))
        self.gridLayout.addWidget(self.lbl_steps_total, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.bar_progress = QtGui.QProgressBar(self.horizontalLayoutWidget_2)
        self.bar_progress.setProperty("value", 0)
        self.bar_progress.setObjectName(_fromUtf8("bar_progress"))
        self.verticalLayout.addWidget(self.bar_progress)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_pause = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.btn_pause.setObjectName(_fromUtf8("btn_pause"))
        self.horizontalLayout.addWidget(self.btn_pause)
        self.btn_unpause = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.btn_unpause.setObjectName(_fromUtf8("btn_unpause"))
        self.horizontalLayout.addWidget(self.btn_unpause)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lbl_dv_folder = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lbl_dv_folder.setReadOnly(True)
        self.lbl_dv_folder.setObjectName(_fromUtf8("lbl_dv_folder"))
        self.gridLayout_2.addWidget(self.lbl_dv_folder, 0, 1, 1, 1)
        self.lineEdit_6 = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit_6.setStyleSheet(_fromUtf8("QLineEdit { background-color: rgb(224,224,224) }"))
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.gridLayout_2.addWidget(self.lineEdit_6, 1, 0, 1, 1)
        self.lineEdit_5 = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lineEdit_5.setStyleSheet(_fromUtf8("QLineEdit { background-color: rgb(224,224,224) }"))
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.gridLayout_2.addWidget(self.lineEdit_5, 0, 0, 1, 1)
        self.lbl_dv_filename = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.lbl_dv_filename.setReadOnly(True)
        self.lbl_dv_filename.setObjectName(_fromUtf8("lbl_dv_filename"))
        self.gridLayout_2.addWidget(self.lbl_dv_filename, 1, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.lineEdit.setText(_translate("MainWindow", "Steps complete", None))
        self.lineEdit_3.setText(_translate("MainWindow", "Steps total", None))
        self.btn_pause.setText(_translate("MainWindow", "Pause", None))
        self.btn_unpause.setText(_translate("MainWindow", "Unpause", None))
        self.lineEdit_6.setText(_translate("MainWindow", "DataVault filename", None))
        self.lineEdit_5.setText(_translate("MainWindow", "DataVault folder", None))

