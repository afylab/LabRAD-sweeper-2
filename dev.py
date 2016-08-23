from PyQt4 import QtCore as core, QtGui as gui
import sys, time
from sweeper import Sweeper

def interval():
	t = time.time()
	yield 0.0
	while True:
		t2 = time.time()
		yield t2-t
		t=t2

class interface(gui.QWidget):

	def __init__(self):
		super(interface,self).__init__()

		self.inputTimer = gui.QLineEdit(self)

		self.buttonGo = gui.QPushButton("go",self)
		self.buttonGo.clicked.connect(self.go)

		self.lay = gui.QVBoxLayout()
		self.lay.addWidget(self.inputTimer)
		self.lay.addWidget(self.buttonGo)
		self.setLayout(self.lay)
		self.show()

		self.s = Sweeper()
		self.s.add_axis(0,1,11)
		self.s.add_axis(0,1,11)
		self.s.add_swept_setting('vds',ID='4000',max_ramp_speed=0.5)
		self.s.add_recorded_setting('vds',ID='4000')
		self.s.initialize_sweep([[0,1,2]], 0.5, 0.025)
		self.going = False

		self.timer = core.QTimer(self)
		self.timer.timeout.connect(self.timer_event)
		self.timer.setInterval(25)
		self.timer.start()

		self.icount = interval()

	def go(self):
		if not self.s.done():
			self.going = True

	def timer_event(self):
		elapsed = self.icount.next()
		if self.going:
			self.s.advance(elapsed,output=False)
			if self.s.done():
				self.going = False

if __name__=='__main__':
	app = gui.QApplication(sys.argv)
	i = interface()
	sys.exit(app.exec_())
