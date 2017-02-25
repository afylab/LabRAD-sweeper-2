# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_rec_bar.ui'
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

class Ui_rec_bar(object):
    def setupUi(self, rec_bar):
        rec_bar.setObjectName(_fromUtf8("rec_bar"))
        rec_bar.resize(201, 21)
        self.horizontalLayoutWidget = QtGui.QWidget(rec_bar)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 201, 22))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lbl_name = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.lbl_name.setReadOnly(True)
        self.lbl_name.setObjectName(_fromUtf8("lbl_name"))
        self.horizontalLayout.addWidget(self.lbl_name)
        self.lbl_units = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.lbl_units.setReadOnly(True)
        self.lbl_units.setObjectName(_fromUtf8("lbl_units"))
        self.horizontalLayout.addWidget(self.lbl_units)
        self.inp_value = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.inp_value.setObjectName(_fromUtf8("inp_value"))
        self.horizontalLayout.addWidget(self.inp_value)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.retranslateUi(rec_bar)
        QtCore.QMetaObject.connectSlotsByName(rec_bar)

    def retranslateUi(self, rec_bar):
        rec_bar.setWindowTitle(_translate("rec_bar", "Form", None))
        self.lbl_name.setPlaceholderText(_translate("rec_bar", "Name", None))
        self.lbl_units.setPlaceholderText(_translate("rec_bar", "Units", None))
        self.inp_value.setPlaceholderText(_translate("rec_bar", "Value", None))

