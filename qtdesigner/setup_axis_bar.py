# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_axis_bar.ui'
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

class Ui_axis_bar(object):
    def setupUi(self, axis_bar):
        axis_bar.setObjectName(_fromUtf8("axis_bar"))
        axis_bar.setWindowModality(QtCore.Qt.NonModal)
        axis_bar.resize(669, 23)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(axis_bar.sizePolicy().hasHeightForWidth())
        axis_bar.setSizePolicy(sizePolicy)
        axis_bar.setMinimumSize(QtCore.QSize(0, 18))
        self.horizontalLayoutWidget_4 = QtGui.QWidget(axis_bar)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(0, 0, 671, 21))
        self.horizontalLayoutWidget_4.setObjectName(_fromUtf8("horizontalLayoutWidget_4"))
        self.bar_layout = QtGui.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.bar_layout.setSpacing(0)
        self.bar_layout.setObjectName(_fromUtf8("bar_layout"))
        self.inp_name = QtGui.QLineEdit(self.horizontalLayoutWidget_4)
        self.inp_name.setObjectName(_fromUtf8("inp_name"))
        self.bar_layout.addWidget(self.inp_name)
        self.inp_start = QtGui.QLineEdit(self.horizontalLayoutWidget_4)
        self.inp_start.setObjectName(_fromUtf8("inp_start"))
        self.bar_layout.addWidget(self.inp_start)
        self.inp_stop = QtGui.QLineEdit(self.horizontalLayoutWidget_4)
        self.inp_stop.setObjectName(_fromUtf8("inp_stop"))
        self.bar_layout.addWidget(self.inp_stop)
        self.inp_points = QtGui.QLineEdit(self.horizontalLayoutWidget_4)
        self.inp_points.setObjectName(_fromUtf8("inp_points"))
        self.bar_layout.addWidget(self.inp_points)
        self.lbl_priority = QtGui.QLineEdit(self.horizontalLayoutWidget_4)
        self.lbl_priority.setReadOnly(True)
        self.lbl_priority.setObjectName(_fromUtf8("lbl_priority"))
        self.bar_layout.addWidget(self.lbl_priority)
        self.btn_up = QtGui.QPushButton(self.horizontalLayoutWidget_4)
        self.btn_up.setObjectName(_fromUtf8("btn_up"))
        self.bar_layout.addWidget(self.btn_up)
        self.btn_down = QtGui.QPushButton(self.horizontalLayoutWidget_4)
        self.btn_down.setObjectName(_fromUtf8("btn_down"))
        self.bar_layout.addWidget(self.btn_down)
        self.btn_del = QtGui.QPushButton(self.horizontalLayoutWidget_4)
        self.btn_del.setObjectName(_fromUtf8("btn_del"))
        self.bar_layout.addWidget(self.btn_del)
        self.bar_layout.setStretch(0, 1)
        self.bar_layout.setStretch(1, 1)
        self.bar_layout.setStretch(2, 1)
        self.bar_layout.setStretch(3, 1)
        self.bar_layout.setStretch(4, 1)
        self.bar_layout.setStretch(5, 1)
        self.bar_layout.setStretch(6, 1)
        self.bar_layout.setStretch(7, 1)

        self.retranslateUi(axis_bar)
        QtCore.QMetaObject.connectSlotsByName(axis_bar)

    def retranslateUi(self, axis_bar):
        axis_bar.setWindowTitle(_translate("axis_bar", "Form", None))
        self.inp_name.setPlaceholderText(_translate("axis_bar", "Name", None))
        self.inp_start.setPlaceholderText(_translate("axis_bar", "Start", None))
        self.inp_stop.setPlaceholderText(_translate("axis_bar", "Stop", None))
        self.inp_points.setPlaceholderText(_translate("axis_bar", "Points", None))
        self.lbl_priority.setPlaceholderText(_translate("axis_bar", "Priority", None))
        self.btn_up.setText(_translate("axis_bar", "Move Up", None))
        self.btn_down.setText(_translate("axis_bar", "Move Down", None))
        self.btn_del.setText(_translate("axis_bar", "Delete Axis", None))

