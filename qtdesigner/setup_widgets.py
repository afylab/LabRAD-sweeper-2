from PyQt4 import QtGui as gui, QtCore as core

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
		self.lbl_priority = gui.QLineEdit(self); self.lbl_priority.setReadOnly(True); self.lbl_priority.setStyleSheet("QLineEdit { background-color: rgb(224,224,224) }")
		self.btn_up       = gui.QPushButton("Move Up",self)
		self.btn_down     = gui.QPushButton("Move down",self)
		self.btn_del      = gui.QPushButton("Delete",self)

		self.layout = gui.QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.addWidget(self.lbl_priority,1)
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
		self.lbl_priority.setText(str(self.priority))
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

class SweptInputBar(gui.QWidget):
	def __init__(self,parent,name='',units=''):
		super(SweptInputBar,self).__init__(parent)
		self.parent=parent

		self.layout = gui.QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)

		self.lbl_name  = gui.QLineEdit(name,self) ; self.lbl_name.setReadOnly(True)
		self.lbl_units = gui.QLineEdit(units,self); self.lbl_units.setReadOnly(True)
		self.inp_value = gui.QLineEdit(self)
		self.cb_sweep  = gui.QCheckBox(self)      ; self.cb_sweep.setEnabled(units == 'v')

		self.layout.addWidget(self.lbl_name , 1)
		self.layout.addWidget(self.lbl_units, 1)
		self.layout.addWidget(self.inp_value, 1)
		self.layout.addWidget(self.cb_sweep , 1)

		# Make these widgets part of the proto_ objects & swap them out
		# .deleteLater when deleting setting, or changing # of inputs
class SweptInputTable(gui.QWidget):
	def __init__(self,parent):
		super(SweptInputTable,self).__init__(parent)
		self.parent=parent

		self.layout = gui.QVBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)

	def set_inputs(self,inputs):
		while self.layout.count() > 0:
			bar = self.layout.takeAt(0)
			try:
				bar.inp_value.textChanged.disconnect()
				bar.ch_sweep.stateChanged.disconnect()
			except:
				pass
			bar.deleteLater()

		bars = []
		for inp in inputs:
			# inp = [name,units]
			bar = SweptInputBar(self,*inp)
			self.layout.addWidget(bar)
			bars.append(bar)
			bar.inp_value.textChanged.connect(self.parent.update_swept_setting_data)
			bar.cb_sweep.stateChanged.connect(self.parent.update_swept_setting_data)

# do it with dialogs
class SweptInputsDialog(gui.QDialog):
	def __init__(self,parent,setting):
		super(SweptInputsDialog,self).__init__(parent)
		self.parent = parent

		acc = setting.accepts[0]
		if acc.startswith('('): acc=acc[1:]
		if acc.endswith(')'):   acc=acc[:-1]
		inputs = [["",u] for u in acc]

		self.setWindowTitle("Setting inputs for {name}".format(name=setting.name))

