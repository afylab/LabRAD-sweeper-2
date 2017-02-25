# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_swp_bar.ui'
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

class Ui_swp_bar(object):
    def setupUi(self, swp_bar):
        swp_bar.setObjectName(_fromUtf8("swp_bar"))
        swp_bar.resize(240, 22)
        self.horizontalLayoutWidget = QtGui.QWidget(swp_bar)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 240, 22))
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
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.cb_sweep = QtGui.QCheckBox(self.horizontalLayoutWidget)
        self.cb_sweep.setText(_fromUtf8(""))
        self.cb_sweep.setObjectName(_fromUtf8("cb_sweep"))
        self.horizontalLayout.addWidget(self.cb_sweep)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 10)
        self.horizontalLayout.setStretch(2, 10)
        self.horizontalLayout.setStretch(3, 4)
        self.horizontalLayout.setStretch(4, 6)

        self.retranslateUi(swp_bar)
        QtCore.QMetaObject.connectSlotsByName(swp_bar)

    def retranslateUi(self, swp_bar):
        swp_bar.setWindowTitle(_translate("swp_bar", "Form", None))
        self.lbl_name.setPlaceholderText(_translate("swp_bar", "Name", None))
        self.lbl_units.setPlaceholderText(_translate("swp_bar", "Units", None))
        self.inp_value.setPlaceholderText(_translate("swp_bar", "Value", None))

