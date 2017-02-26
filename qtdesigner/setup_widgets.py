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
		self.lbl_priority = gui.QLineEdit(self); self.lbl_priority.setReadOnly(True)
		self.btn_up       = gui.QPushButton("Move Up",self)
		self.btn_down     = gui.QPushButton("Move down",self)
		self.btn_del      = gui.QPushButton("Delete",self)

		self.layout = gui.QHBoxLayout()
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.addWidget(self.inp_name,1)
		self.layout.addWidget(self.inp_start,1)
		self.layout.addWidget(self.inp_stop,1)
		self.layout.addWidget(self.inp_points,1)
		self.layout.addWidget(self.lbl_priority,1)
		self.layout.addWidget(self.btn_up,1)
		self.layout.addWidget(self.btn_down,1)
		self.layout.addWidget(self.btn_del,1)

		if name:self.inp_name.setText(name)
		self.set_priority(priority)

		self.setLayout(self.layout)

		self.btn_down.clicked.connect(self.move_down)
		self.btn_up.clicked.connect(self.move_up)
		self.btn_del.clicked.connect(self.delete)

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


	def move_up(self):
		if self.priority == 0:return

		self.parent.layout_axis_list.removeWidget(self)
		self.parent.layout_axis_list.removeWidget(self.parent.axes[self.priority-1])

		self.parent.axes[self.priority],self.parent.axes[self.priority-1] = self.parent.axes[self.priority-1],self.parent.axes[self.priority]
		self.parent.axes[self.priority].set_priority(self.priority)
		self.set_priority(self.priority-1)

		self.parent.layout_axis_list.insertWidget(self.priority,self)
		self.parent.layout_axis_list.insertWidget(self.priority+1,self.parent.axes[self.priority+1])
	
	def delete(self):
		self.parent.layout_axis_list.removeWidget(self)
		self.parent.axes.pop(self.priority)
		for n in range(self.priority,len(self.parent.axes)):
			self.parent.axes[n].set_priority(self.parent.axes[n].priority-1)
		self.deleteLater()
		self.parent.update_axis_count()
