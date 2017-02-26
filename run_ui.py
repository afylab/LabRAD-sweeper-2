import sys,labrad
from PyQt4 import QtGui as gui, QtCore as core
from qtdesigner import setup#,setup_axis_bar,setup_rec_bar,setup_swp_bar
from qtdesigner.setup_widgets import AxisBar
from labrad_exclude import SERVERS,SETTINGS

def get_is_sweepable(setting):
	"""determines if a setting can be swept"""
	return True # placeholder

def get_is_recordable(setting):
	"""determines if a setting can be recorded"""
	return True # placeholder

class SetupWindow(gui.QMainWindow,setup.Ui_setup):
	def __init__(self,parent=None):
		super(SetupWindow,self).__init__(parent)
		self.setupUi(self)

		self.labrad_connect() # connect to LabRAD, fetch servers/devices, etc
		self.rig() # hook UI to functionality

	def labrad_connect(self):
		self._cxn = labrad.connect()
		self.refresh_lists()

	def refresh_lists(self):
		"""Fetches servers, devices, settings, etc. from LabRAD"""
		self.servers = [server for server in [str(s) for s in self._cxn.servers] if not (server in SERVERS)]
		print("Found servers: {s}".format(s=self.servers))

		self.devices = {}
		for server in self.servers:
			try:
				devices = self._cxn.servers[server].list_devices()
			except:
				print("Error: tried to collect devices from non-device server {s}. You may want to add it to the excluded servers list, found in labrad_exclude.py".format(s=server))
			if len(devices) == 0:
				print("Warning: server {s} has no active devices.".format(s=server))
			self.devices.update([ [server,devices] ])
		print("found devices: {d}".format(d=self.devices))

		self.settings = {}
		for server in self.servers:
			swp_settings = []
			rec_settings = []
			for setting in self._cxn.servers[server].settings:
				if setting.startswith('signal__'):continue
				if setting in SETTINGS[server]:continue
				if get_is_sweepable(self._cxn.servers[server].settings[setting]):swp_settings.append(setting)
				if get_is_recordable(self._cxn.servers[server].settings[setting]):rec_settings.append(setting)
			self.settings.update([ [server,[swp_settings,rec_settings]] ])

		print('\n')
			


	def rig(self):
		"""This function connects the UI elements to each other, and to the sweeper code."""

		# INTERNAL OBJECTS
		self.axes              = [] # 
		self.swept_settings    = [] # 
		self.recorded_settings = [] # 
		self.comments          = [] # [ [author, body], ... ]
		self.parameters        = [] # [ [name, units, value], ... ]

		# Axis creation
		self.axes_btn_add.clicked.connect(self.add_axis)
		self.update_axis_count()

		# Add/remove parameters
		self.par_btn_add.clicked.connect(self.add_parameter)
		self.par_btn_del.clicked.connect(self.del_parameter)

		# Add/remove comments
		self.com_btn_add.clicked.connect(self.add_comment)
		self.com_btn_del.clicked.connect(self.del_comment)


	# managing comments
	def add_comment(self):
		author = str(self.com_inp_author.text())
		body   = str(self.com_inp_body.toPlainText())
		if not author: author = 'user'
		if not body:
			print("Error: comment cannot be blank")
			return
		self.comments.append([author,body])
		self.update_comment_list()
	def del_comment(self):
		which = int(self.com_list_comments.currentRow())
		if which >= 0:
			self.comments.pop(which)
			self.update_comment_list()
	def update_comment_list(self):
		self.com_list_comments.clear()
		for c in self.comments:
			self.com_list_comments.addItem("({a}) - {b}".format(a=c[0],b=c[1]))


	# managing parameters
	def add_parameter(self):
		name  = str(self.par_inp_name.text())
		units = str(self.par_inp_units.text())
		value = str(self.par_inp_value.text())
		if not name:
			print("Error: name cannot be blank")
			return
		if name in [p[0] for p in self.parameters]:
			print("Error: name cannot be same as existing parameter")
			return
		if not units:
			print("Error: units cannot be blank")
			return
		try:
			value = float(value)
		except:
			print("Error: value must be interpretable as a float")
			return
		self.parameters.append([name,units,value])
		self.update_parameter_list()
	def del_parameter(self):
		which = int(self.par_list_parameters.currentRow())
		if which >= 0:
			self.parameters.pop(which)
			self.update_parameter_list()
	def update_parameter_list(self):
		self.par_list_parameters.clear()
		for p in self.parameters:
			self.par_list_parameters.addItem("{n}: {v} {u}".format(n=p[0],u=p[1],v=p[2]))


	# managing axes
	def add_axis(self):
		# adds an axis to the list, if there are fewer than 6
		if len(self.axes) >= 6:
			print("Error: max axis count is 6")
			return
		new_axis = AxisBar(self,len(self.axes),"Axis {n}".format(n=len(self.axes)))
		self.axes.append(new_axis)
		self.layout_axis_list.addWidget(new_axis,1)
		self.update_axis_count()
	def update_axis_count(self):
		# hides/shows axis specific inputs based on number of axes present
		coeff_labels = [self.swp_lbl_coeff_0,self.swp_lbl_coeff_1,self.swp_lbl_coeff_2,self.swp_lbl_coeff_3,self.swp_lbl_coeff_4,self.swp_lbl_coeff_5]
		coeff_inputs = [self.swp_inp_coeff_0,self.swp_inp_coeff_1,self.swp_inp_coeff_2,self.swp_inp_coeff_3,self.swp_inp_coeff_4,self.swp_inp_coeff_5]
		ignore_cb    = [self.rec_cb_ignore_0,self.rec_cb_ignore_1,self.rec_cb_ignore_2,self.rec_cb_ignore_3,self.rec_cb_ignore_4,self.rec_cb_ignore_5]
		for n in range(6):
			coeff_labels[n].setHidden(n>=len(self.axes))
			coeff_inputs[n].setHidden(n>=len(self.axes))
			ignore_cb[n].setHidden(n>=len(self.axes))


	# Functions for hiding/showing parts of UI
	def set_vis(self,widgets,vis):
		for widget in widgets:widget.setHidden(not vis)
	def vis_swp_labrad(self,vis):
		set_vis([
			self.swp_lbl_rad,
			self.swp_lbl_rad_inp_name,
			self.swp_lbl_rad_inp_units,
			self.swp_lbl_rad_inp_value,
			self.swp_lbl_rad_inp_sweep,
			self.swp_lbl_rad_server,
			self.swp_lbl_rad_device,
			self.swp_lbl_rad_setting,
			self.swp_dd_rad_server,
			self.swp_dd_rad_device,
			self.swp_dd_rad_setting,
			],vis)
	def vis_swp_vds(self,vis):
		set_vis([
			self.swp_lbl_vds,
			self.swp_lbl_vds_name,
			self.swp_lbl_vds_id,
			self.swp_dd_vds,
			self.swp_inp_vds_name,
			self.swp_inp_vds_id,
			],vis)
	def vis_swp_builtin(self,vis):
		set_vis([
			self.swp_lbl_builtins,
			self.swp_dd_builtins,
			],vis)
	def vis_rec_labrad(self,vis):
		set_vis([
			self.rec_lbl_rad,
			self.rec_lbl_rad_inp_name,
			self.rec_lbl_rad_inp_units,
			self.rec_lbl_rad_inp_value,
			self.rec_lbl_rad_server,
			self.rec_lbl_rad_device,
			self.rec_lbl_rad_setting,
			self.rec_dd_rad_server,
			self.rec_dd_rad_device,
			self.rec_dd_rad_setting,
			],vis)
	def vis_rec_vds(self,vis):
		set_vis([
			self.rec_lbl_vds,
			self.rec_lbl_vds_name,
			self.rec_lbl_vds_id,
			self.rec_dd_vds,
			self.rec_inp_vds_name,
			self.rec_inp_vds_id,
			],vis)
	def vis_rec_builtin(self,vis):
		set_vis([
			self.rec_lbl_builtins,
			self.rec_dd_builtins,
			],vis)

if __name__=='__main__':
    app = gui.QApplication(sys.argv)
    i = SetupWindow()
    i.show()
    sys.exit(app.exec_())