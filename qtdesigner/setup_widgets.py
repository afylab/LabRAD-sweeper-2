from PyQt4 import QtGui as gui, QtCore as core

strn = lambda s:str(s) if not (s is None) else ""

is_sweepable = lambda units:units=='v'

def validate_int(text):
	text = str(text)
	try:
		int(text)
		return True
	except:
		return False
def validate_float(text):
	text = str(text)
	try:
		float(text)
		return True
	except:
		return False

class AxisBar(gui.QWidget):
	def __init__(self,parent,priority,name=None):
		super(AxisBar,self).__init__(parent)
		self.parent = parent

		self.priority=priority

		self.inp_name     = gui.QLineEdit(self)
		self.inp_start    = gui.QLineEdit(self)
		self.inp_stop     = gui.QLineEdit(self)
		self.inp_points   = gui.QLineEdit(self)
		self.inp_delay    = gui.QLineEdit(self)
		self.header_priority = gui.QLineEdit(self); self.header_priority.setReadOnly(True); self.header_priority.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.btn_up       = gui.QPushButton("Move Up",self)
		self.btn_down     = gui.QPushButton("Move down",self)
		self.btn_del      = gui.QPushButton("Delete",self)

		self.layout = gui.QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.addWidget(self.header_priority,1)
		self.layout.addWidget(self.inp_name,2)
		self.layout.addWidget(self.inp_start,2)
		self.layout.addWidget(self.inp_stop,2)
		self.layout.addWidget(self.inp_points,2)
		self.layout.addWidget(self.inp_delay,2)
		self.layout.addWidget(self.btn_up,2)
		self.layout.addWidget(self.btn_down,2)
		self.layout.addWidget(self.btn_del,2)

		if name:self.inp_name.setText(name)
		self.set_priority(priority)

		self.setLayout(self.layout)

		self.btn_down.clicked.connect(self.move_down)
		self.btn_up.clicked.connect(self.move_up)
		self.btn_del.clicked.connect(self.delete)

		self.inp_start.textEdited.connect(self.parent.check_axes)
		self.inp_stop.textEdited.connect(self.parent.check_axes)
		self.inp_points.textEdited.connect(self.parent.check_axes)
		self.inp_delay.textEdited.connect(self.parent.check_axes)
		self.inp_name.textEdited.connect(self.parent.check_axes)

	def set_priority(self,priority):
		if str(self.inp_name.text()) == "Axis {n}".format(n=self.priority):
			self.inp_name.setText("Axis {n}".format(n=priority))

		self.priority = priority
		self.header_priority.setText(str(self.priority))
	def move_down(self):
		if self.priority >= len(self.parent.axes)-1: return

		self.parent.layout_axis_list.removeWidget(self)
		self.parent.layout_axis_list.removeWidget(self.parent.axes[self.priority+1])

		self.parent.axes[self.priority],self.parent.axes[self.priority+1] = self.parent.axes[self.priority+1],self.parent.axes[self.priority]
		self.parent.axes[self.priority].set_priority(self.priority)
		self.set_priority(self.priority+1)

		self.parent.layout_axis_list.insertWidget(self.priority-1,self.parent.axes[self.priority-1])
		self.parent.layout_axis_list.insertWidget(self.priority,self)
		self.parent.check_axes()
	def move_up(self):
		if self.priority == 0:return

		self.parent.layout_axis_list.removeWidget(self)
		self.parent.layout_axis_list.removeWidget(self.parent.axes[self.priority-1])

		self.parent.axes[self.priority],self.parent.axes[self.priority-1] = self.parent.axes[self.priority-1],self.parent.axes[self.priority]
		self.parent.axes[self.priority].set_priority(self.priority)
		self.set_priority(self.priority-1)

		self.parent.layout_axis_list.insertWidget(self.priority,self)
		self.parent.layout_axis_list.insertWidget(self.priority+1,self.parent.axes[self.priority+1])
		self.parent.check_axes()
	def delete(self):
		self.parent.layout_axis_list.removeWidget(self)
		self.parent.axes.pop(self.priority)
		for n in range(self.priority,len(self.parent.axes)):
			self.parent.axes[n].set_priority(self.parent.axes[n].priority-1)

		self.btn_down.clicked.disconnect()
		self.btn_up.clicked.disconnect()
		self.btn_del.clicked.disconnect()

		self.inp_start.textEdited.disconnect()
		self.inp_stop.textEdited.disconnect()
		self.inp_points.textEdited.disconnect()
		self.inp_delay.textEdited.disconnect()
		self.inp_name.textEdited.disconnect()

		self.deleteLater()
		self.parent.update_axis_count()

class InputDialogSwept(gui.QDialog):
	def __init__(self,inputs,slot,parent=None):
		""""""
		# inputs is a list of [ [name,units,value] ]
		# value = None if not yet specified
		super(InputDialogSwept,self).__init__(parent)

		self.setWindowTitle("Inputs for swept setting")

		n_inputs = len(inputs)

		self.grid = gui.QGridLayout(self)
		self.grid.setContentsMargins(0,0,0,0)
		self.grid.setSpacing(0)

		self.header_name  = gui.QLineEdit("name"  ,self); self.header_name.setReadOnly(True) ; self.grid.addWidget(self.header_name ,0,0)
		self.header_units = gui.QLineEdit("units" ,self); self.header_units.setReadOnly(True); self.grid.addWidget(self.header_units,0,1)
		self.header_value = gui.QLineEdit("value" ,self); self.header_value.setReadOnly(True); self.grid.addWidget(self.header_value,0,2)
		self.header_sweep = gui.QLineEdit("sweep?",self); self.header_sweep.setReadOnly(True); self.grid.addWidget(self.header_sweep,0,3)
		self.header_name.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.header_units.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.header_value.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.header_sweep.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")

		self.lbl_name  = [] # list of LineEdit objects that are input name  labels
		self.lbl_units = [] # list of LineEdit objects that are input units labels
		self.inp_value = [] # list of LineEdit objects that are input value inputs
		self.cb_sweep  = [] # list of CheckBox objects (or None it input is not sweepable)

		first_button = True

		for n in range(n_inputs):
			lbl_name  = gui.QLineEdit(strn(inputs[n][0]),self); lbl_name.setReadOnly(True) ; self.grid.addWidget(lbl_name ,n+1,0); self.lbl_name.append(lbl_name)
			lbl_units = gui.QLineEdit(strn(inputs[n][1]),self); lbl_units.setReadOnly(True); self.grid.addWidget(lbl_units,n+1,1); self.lbl_units.append(lbl_units)
			inp_value = gui.QLineEdit(strn(inputs[n][2]),self);                              self.grid.addWidget(inp_value,n+1,2); self.inp_value.append(inp_value)
			inp_value.textEdited.connect(self.validate)
			if not(is_sweepable(inputs[n][1])):
				self.cb_sweep.append(None)
				self.grid.addItem(gui.QSpacerItem(0,0),n+1,3)
			else:
				cb_sweep = gui.QRadioButton(self)
				cb_sweep.clicked.connect(lambda:cb_sweep.setChecked(True)) # By default with Radio Buttons, clicking the active one deactivates it so that none are checked. This disables that behavior.
				cb_sweep.clicked.connect(self.validate)
				cb_sweep.clicked.connect(self.update_value_inputs)
				self.cb_sweep.append(cb_sweep)
				if first_button:
					if slot is None:cb_sweep.setChecked(True)
					first_button=False
				self.grid.addWidget(cb_sweep,n+1,3)

		if not (slot is None):
			try:
				self.cb_sweep[slot].setChecked(True)
			except:
				for obj in self.cb_sweep:
					if not (obj is None):
						obj.setChecked(True)
						break

		self.btn_accept = gui.QPushButton("accept",self); self.btn_accept.clicked.connect(self.accept)
		self.btn_cancel = gui.QPushButton("cancel",self); self.btn_cancel.clicked.connect(self.reject)
		self.grid.addWidget(self.btn_accept,n+2,2)
		self.grid.addWidget(self.btn_cancel,n+2,3)

		self.setLayout(self.grid)
		self.update_value_inputs()
		self.validate()
	def validate(self):
		for n in range(len(self.inp_value)):

			if not (self.cb_sweep[n] is None):
				if self.cb_sweep[n].isChecked():
					continue

			if str(self.lbl_units[n].text()) == 'i':
				if not(validate_int(self.inp_value[n].text())):
					self.btn_accept.setEnabled(False)
					return

			if str(self.lbl_units[n].text()) == 'v':
				if not(validate_float(self.inp_value[n].text())):
					self.btn_accept.setEnabled(False)
					return

		self.btn_accept.setEnabled(True)
	def update_value_inputs(self):
		for n in range(len(self.cb_sweep)):
			if not (self.cb_sweep[n] is None):
				self.inp_value[n].setEnabled(not self.cb_sweep[n].isChecked())
	def values(self):
		return [str(self.inp_value[n].text()) for n in range(len(self.inp_value))]
	def sweepSlot(self):
		for n in range(len(self.cb_sweep)):
			if self.cb_sweep[n] is None:continue
			if self.cb_sweep[n].isChecked():return n
		return None

	@staticmethod
	def getInputs(inputs,slot,parent=None):
		dialog = InputDialogSwept(inputs,slot,parent)
		result = dialog.exec_()
		return [dialog.values(),dialog.sweepSlot(),result==gui.QDialog.Accepted]

class InputDialogRecorded(gui.QDialog):
	def __init__(self,inputs,parent=None):
		super(InputDialogRecorded,self).__init__(parent)
		self.setWindowTitle("Inputs for recorded setting")

		n_inputs = len(inputs)

		self.grid = gui.QGridLayout()
		self.grid.setContentsMargins(0,0,0,0)
		self.grid.setSpacing(0)

		self.header_name  = gui.QLineEdit("name"  ,self); self.header_name.setReadOnly(True) ; self.grid.addWidget(self.header_name ,0,0)
		self.header_units = gui.QLineEdit("units" ,self); self.header_units.setReadOnly(True); self.grid.addWidget(self.header_units,0,1)
		self.header_value = gui.QLineEdit("value" ,self); self.header_value.setReadOnly(True); self.grid.addWidget(self.header_value,0,2)
		self.header_name.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.header_units.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.header_value.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")

		self.lbl_name  = []
		self.lbl_units = []
		self.inp_value = []

		for n in range(n_inputs):
			lbl_name  = gui.QLineEdit(strn(inputs[n][0]),self); lbl_name.setReadOnly(True) ; self.grid.addWidget(lbl_name ,n+1,0); self.lbl_name.append(lbl_name)
			lbl_units = gui.QLineEdit(strn(inputs[n][1]),self); lbl_units.setReadOnly(True); self.grid.addWidget(lbl_units,n+1,1); self.lbl_units.append(lbl_units)
			inp_value = gui.QLineEdit(strn(inputs[n][2]),self);                              self.grid.addWidget(inp_value,n+1,2); self.inp_value.append(inp_value)
			inp_value.textEdited.connect(self.validate)

		self.btn_accept = gui.QPushButton("accept",self); self.btn_accept.clicked.connect(self.accept)
		self.btn_cancel = gui.QPushButton("cancel",self); self.btn_cancel.clicked.connect(self.reject)
		self.grid.addWidget(self.btn_accept,n+2,1)
		self.grid.addWidget(self.btn_cancel,n+2,2)

		self.setLayout(self.grid)
		self.validate()
	def validate(self):
		for n in range(len(self.inp_value)):

			if str(self.lbl_units[n].text()) == 'i':
				if not(validate_int(self.inp_value[n].text())):
					self.btn_accept.setEnabled(False)
					return

			if str(self.lbl_units[n].text()) == 'v':
				if not(validate_float(self.inp_value[n].text())):
					self.btn_accept.setEnabled(False)
					return

		self.btn_accept.setEnabled(True)
	def values(self):
		return [str(self.inp_value[n].text()) for n in range(len(self.inp_value))]

	@staticmethod
	def getInputs(inputs,parent=None):
		dialog = InputDialogRecorded(inputs,parent)
		result = dialog.exec_()
		return [dialog.values(),result==gui.QDialog.Accepted]
