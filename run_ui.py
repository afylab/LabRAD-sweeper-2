import sys,labrad
from PyQt4 import QtGui as gui, QtCore as core
from qtdesigner import setup#,setup_axis_bar,setup_rec_bar,setup_swp_bar
from qtdesigner.setup_widgets import AxisBar,SweptInputTable#,RecordedInputBar
from labrad_exclude import SERVERS,SETTINGS

class proto_swept_setting(object):
	"""Houses the data associated with a swept setting that hasn't been added to a sweep yet"""
	def __init__(self,n):
		self.label = "swept setting {n}".format(n=n) # Default label is swept setting n.
		self.type  = "VDS" # Defaults to VDS setting
		self.coeff = [0,0,0,0,0,0,0]
		self.builtin_type = None
		self.vds_dd       = None
		self.vds_name     = ""
		self.vds_id       = ""
		self.rad_server     = -1 # -1 = none selected
		self.rad_device     = -1 #
		self.rad_setting    = -1 # 
		self.rad_input_count = 0
		self.rad_inputs      = [] # list of [[input,sweep?],...]
class proto_recorded_setting(object):
	"""Houses the data associated with a recorded setting that hasn't been added to a sweep yet"""
	def __init__(self,n):
		self.label  = "recorded setting {n}".format(n=n)
		self.type   = "VDS"
		self.ignore = [False,False,False,False,False,False]
		self.builtin_type = None
		self.vds_dd       = None
		self.vds_name     = ""
		self.vds_id       = ""
		self.rad_server     = -1
		self.rad_device     = -1
		self.rad_setting    = -1
		self.rad_input_count = 0
		self.rad_inputs     = [] # list of input values


def get_is_sweepable(setting):
	"""determines if a setting can be swept"""
	if len(setting.accepts) == 0:return False
	if 'v' in setting.accepts[0]:return True
	return False
def get_is_recordable(setting):
	"""determines if a setting can be recorded"""
	if len(setting.returns) == 0:return False
	if 'v' in setting.returns[0]:return True
	return False


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
		# Called once upon start-up, will later be added as hotkey (ctrl+r probably.)

		# Get servers, exclude those found in labrad_exclude.py, as well as any ending in "_serial_server" (assumed to be serial servers.)
		self.servers = [server for server in [str(s) for s in self._cxn.servers] if not (server in SERVERS or server.endswith("_serial_server"))]
		print("Found servers: {s}".format(s=self.servers))

		self.devices = {} # Dict of server:[devices] for servers found to have a list_devices() function.
		bad_servers = []  # List to be populated with servers that don't have a list_devices() function. These will be removed from the server list.
		for server in self.servers:
			try:
				devices = self._cxn.servers[server].list_devices()
				if len(devices) == 0:
					print("Warning: server {s} has no active devices.".format(s=server))
				self.devices.update([ [server,devices] ])
			except:
				print("Error: tried to collect devices from non-device server {s}. You may want to add it to the excluded servers list, found in labrad_exclude.py".format(s=server))
				bad_servers.append(server)

		# remove servers that aren't device servers
		self.servers = [s for s in self.servers if not(s in bad_servers)]
		print("found valid servers: {s}".format(s=self.servers))
		print("found devices: {d}".format(d=self.devices))

		# fetch settings per server, ignoring those found in labrad_exclude.py, and only keeping those that are valid to either sweep, record, or both.
		self.settings = {}
		for server in self.servers:
			swp_settings = []
			rec_settings = []
			for setting in self._cxn.servers[server].settings:
				if setting.startswith('signal__'):continue
				if server in SETTINGS.keys():
					if setting in SETTINGS[server]:continue
				if get_is_sweepable(self._cxn.servers[server].settings[setting]):swp_settings.append(setting)
				if get_is_recordable(self._cxn.servers[server].settings[setting]):rec_settings.append(setting)
			self.settings.update([ [server,[swp_settings,rec_settings]] ])

		# Populate server dropdowns with servers that have relevant settings
		self.swp_dd_rad_server.addItems([s for s in self.servers if len(self.settings[s][0])>0])
		self.rec_dd_rad_server.addItems([s for s in self.servers if len(self.settings[s][1])>0])

		# VDS
		if not("virtual_device_server" in self._cxn.servers):
			print("Warning: Virtual Device Server not found.")
			self.vds_channels = []
			self.vds_swp      = []
			self.vds_rec      = []
		else:
			self.vds_channels = self._cxn.virtual_device_server.list_channels()
			self.vds_swp = [c for c in self.vds_channels if self._cxn.virtual_device_server.list_channel_details(c[0])[6]]
			self.vds_rec = [c for c in self.vds_channels if self._cxn.virtual_device_server.list_channel_details(c[0])[5]]
		self.swp_dd_vds.clear()
		self.rec_dd_vds.clear()
		self.swp_dd_vds.addItems([c[1] for c in self.vds_swp])
		self.rec_dd_vds.addItems([c[1] for c in self.vds_rec])




		print('\n')


	def rig(self):
		"""This function connects the UI elements to each other, and to the sweeper code."""

		# INTERNAL OBJECTS
		self.axes                   = [] # 
		self.swept_settings         = [] # 
		self.swept_labrad_inputs    = [] # [ labrad_swp_input_bar, ... ]
		self.recorded_settings      = [] # 
		self.recorded_labrad_inputs = [] # [ labrad_rec_input_bar, ... ]
		self.comments               = [] # [ [author, body], ... ]
		self.parameters             = [] # [ [name, units, value], ... ]

		self.type_index    = {"":-1,None:-1,"VDS":0,"LabRAD":1,"Builtin":2}
		self.builtin_index = {"":-1,None:-1}

		# Axis creation
		self.axes_btn_add.clicked.connect(self.add_axis)
		self.update_axis_count()

		# Add/remove parameters
		self.par_btn_add.clicked.connect(self.add_parameter)
		self.par_btn_del.clicked.connect(self.del_parameter)

		# Add/remove comments
		self.com_btn_add.clicked.connect(self.add_comment)
		self.com_btn_del.clicked.connect(self.del_comment)

		# swept settings
		self.swp_btn_add.clicked.connect(self.add_swept_setting)
		self.swp_btn_del.clicked.connect(self.del_swept_setting)
		self.swp_list_settings.currentRowChanged.connect(self.fetch_swept_setting_data)

		self.swp_dd_vds.activated.connect(self.update_swept_vds_data)
		self.swp_inp_label.textChanged.connect(self.update_swept_setting_name)
		self.swp_dd_type.currentIndexChanged.connect(self.update_swept_setting_type)

		self.swp_dd_rad_server.currentIndexChanged.connect(self.update_swp_rad_dds)

		self.swp_inp_label.textChanged.connect(self.update_swept_setting_data)
		self.swp_dd_type.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_dd_builtins.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_dd_vds.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_inp_vds_name.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_vds_id.textChanged.connect(self.update_swept_setting_data)
		self.swp_dd_rad_server.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_dd_rad_device.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_dd_rad_setting.currentIndexChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_const.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_0.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_1.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_2.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_3.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_4.textChanged.connect(self.update_swept_setting_data)
		self.swp_inp_coeff_5.textChanged.connect(self.update_swept_setting_data)

		self.swp_input_table = SweptInputTable(self)
		self.swp_lay_rad_inp.addWidget(self.swp_input_table)

		# recorded settings
		self.rec_btn_add.clicked.connect(self.add_recorded_setting)
		self.rec_btn_del.clicked.connect(self.del_recorded_setting)
		self.rec_list_settings.currentRowChanged.connect(self.fetch_recorded_setting_data)

		self.rec_dd_vds.activated.connect(self.update_recorded_vds_data)
		self.rec_inp_label.textChanged.connect(self.update_recorded_setting_name)
		self.rec_dd_type.currentIndexChanged.connect(self.update_recorded_setting_type)
		self.rec_btn_ignore_all.clicked.connect(self.rec_ignore_all)

		self.rec_dd_rad_server.currentIndexChanged.connect(self.update_rec_rad_dds)

		self.rec_inp_label.textChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_type.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_builtins.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_vds.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_inp_vds_name.textChanged.connect(self.update_recorded_setting_data)
		self.rec_inp_vds_id.textChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_rad_server.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_rad_device.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_dd_rad_setting.currentIndexChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_0.stateChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_1.stateChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_2.stateChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_3.stateChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_4.stateChanged.connect(self.update_recorded_setting_data)
		self.rec_cb_ignore_5.stateChanged.connect(self.update_recorded_setting_data)

		self.vis_swp(False)
		self.vis_rec(False)


	# recorded settings functions
	def add_recorded_setting(self):
		n=len(self.recorded_settings)
		rec=proto_recorded_setting(n)
		self.recorded_settings.append(rec)
		self.rec_list_settings.addItem(rec.label)
	def del_recorded_setting(self):
		if len(self.recorded_settings)==0:return
		n=self.rec_list_settings.currentRow()
		if n>=0:
			reselect = (n != len(self.recorded_settings)-1)
			self.recorded_settings.pop(n)
			self.rec_list_settings.takeItem(n)
			if reselect:self.fetch_recorded_setting_data()
	def fetch_recorded_setting_data(self):
		n = self.rec_list_settings.currentRow()
		if n == -1:
			self.vis_rec(False)
			return
		if n >= len(self.recorded_settings):return

		label    = self.recorded_settings[n].label
		_type    = self.type_index[self.recorded_settings[n].type]
		builtin  = self.builtin_index[self.recorded_settings[n].builtin_type]
		vds_name = self.recorded_settings[n].vds_name
		vds_id   = self.recorded_settings[n].vds_id
		i0       = self.recorded_settings[n].ignore[0]
		i1       = self.recorded_settings[n].ignore[1]
		i2       = self.recorded_settings[n].ignore[2]
		i3       = self.recorded_settings[n].ignore[3]
		i4       = self.recorded_settings[n].ignore[4]
		i5       = self.recorded_settings[n].ignore[5]
		rad_server  = self.recorded_settings[n].rad_server
		rad_device  = self.recorded_settings[n].rad_device
		rad_setting = self.recorded_settings[n].rad_setting

		self.rec_inp_label.setText(label)
		self.rec_dd_type.setCurrentIndex(_type)
		self.rec_dd_vds.setCurrentIndex(-1)
		self.rec_dd_builtins.setCurrentIndex(builtin)
		self.rec_inp_vds_name.setText(vds_name)
		self.rec_inp_vds_id.setText(vds_id)
		self.rec_cb_ignore_0.setChecked(i0)
		self.rec_cb_ignore_1.setChecked(i1)
		self.rec_cb_ignore_2.setChecked(i2)
		self.rec_cb_ignore_3.setChecked(i3)
		self.rec_cb_ignore_4.setChecked(i4)
		self.rec_cb_ignore_5.setChecked(i5)

		self.rec_dd_rad_server.setCurrentIndex(rad_server)
		self.rec_dd_rad_device.setCurrentIndex(rad_device)
		self.rec_dd_rad_setting.setCurrentIndex(rad_setting)

		self.vis_rec(True)
		self.update_recorded_setting_type()
	def update_recorded_vds_data(self):
		c = self.vds_rec[self.rec_dd_vds.currentIndex()]
		self.rec_inp_vds_name.setText(c[1])
		self.rec_inp_vds_id.setText(c[0])
	def update_recorded_setting_name(self,name):
		if self.rec_list_settings.currentRow() == -1:return
		self.rec_list_settings.currentItem().setText(name)
	def update_recorded_setting_type(self):
		t = str(self.rec_dd_type.currentText())
		self.vis_rec_labrad(t=='LabRAD')
		self.vis_rec_vds(t=='VDS')
		self.vis_rec_builtin(t=='Builtin')
	def update_recorded_setting_data(self):
		n = self.rec_list_settings.currentRow()
		if n == -1:return
		
		if str(self.rec_inp_label.text()) != "":self.recorded_settings[n].label = str(self.rec_inp_label.text())
		self.recorded_settings[n].type         = str(self.rec_dd_type.currentText())
		self.recorded_settings[n].builtin_type = str(self.rec_dd_builtins.currentText())
		self.recorded_settings[n].vds_name     = str(self.rec_inp_vds_name.text())
		self.recorded_settings[n].vds_id       = str(self.rec_inp_vds_id.text())
		self.recorded_settings[n].vds_dd       = str(self.rec_dd_vds.currentText())
		self.recorded_settings[n].rad_server   = self.rec_dd_rad_server.currentIndex()
		self.recorded_settings[n].rad_device   = self.rec_dd_rad_device.currentIndex()
		self.recorded_settings[n].rad_setting  = self.rec_dd_rad_setting.currentIndex()
		self.recorded_settings[n].ignore       = [self.rec_cb_ignore_0.isChecked(),self.rec_cb_ignore_1.isChecked(),self.rec_cb_ignore_2.isChecked(),self.rec_cb_ignore_3.isChecked(),self.rec_cb_ignore_4.isChecked(),self.rec_cb_ignore_5.isChecked()]
		self.recorded_settings[n].rad_inputs   = [str(self.recorded_labrad_inputs[k].inp_value.text()) for k in range(self.recorded_settings[n].rad_input_count)]
	def rec_ignore_all(self):
		if self.rec_list_settings.currentRow() == -1:return
		all_ignored = all([self.rec_cb_ignore_0.isChecked(),self.rec_cb_ignore_1.isChecked(),self.rec_cb_ignore_2.isChecked(),self.rec_cb_ignore_3.isChecked(),self.rec_cb_ignore_4.isChecked(),self.rec_cb_ignore_5.isChecked()])
		self.rec_cb_ignore_0.setChecked(not all_ignored)
		self.rec_cb_ignore_1.setChecked(not all_ignored)
		self.rec_cb_ignore_2.setChecked(not all_ignored)
		self.rec_cb_ignore_3.setChecked(not all_ignored)
		self.rec_cb_ignore_4.setChecked(not all_ignored)
		self.rec_cb_ignore_5.setChecked(not all_ignored)
	def update_rec_rad_dds(self):
		s = str(self.rec_dd_rad_server.currentText())
		self.rec_dd_rad_device.clear()
		self.rec_dd_rad_setting.clear()
		if s == '':return

		if len(self.devices[s]) == 0:
			print("Warning: selected server has no devices")
		else:
			self.rec_dd_rad_device.addItems([d[1] for d in self.devices[s]])

		if len(self.settings[s][1])==0:
			print("Warning: selected setver has no recordable settings")
		else:
			self.rec_dd_rad_setting.addItems(self.settings[s][1])

		self.rec_dd_rad_device.setCurrentIndex(-1)
		self.rec_dd_rad_setting.setCurrentIndex(-1)

	# swept setting functions
	def add_swept_setting(self):
		n = len(self.swept_settings)
		swp = proto_swept_setting(n)
		self.swept_settings.append(swp)
		self.swp_list_settings.addItem(swp.label)
	def del_swept_setting(self):
		if len(self.swept_settings) == 0:return
		n=self.swp_list_settings.currentRow()
		if n>=0:
			reselect = (n != len(self.swept_settings)-1)
			self.swept_settings.pop(n)
			self.swp_list_settings.takeItem(n)
			if reselect:self.fetch_swept_setting_data()
	def fetch_swept_setting_data(self):
		"""writes the newly selected setting's data to the input fields"""
		n = self.swp_list_settings.currentRow()
		if n == -1:
			self.vis_swp(False)
			return
		if n >= len(self.swept_settings):return

		label    = self.swept_settings[n].label
		_type    = self.type_index[self.swept_settings[n].type]
		builtin  = self.builtin_index[self.swept_settings[n].builtin_type]
		vds_name = self.swept_settings[n].vds_name
		vds_id   = self.swept_settings[n].vds_id
		cc = str(self.swept_settings[n].coeff[0])
		c0 = str(self.swept_settings[n].coeff[1])
		c1 = str(self.swept_settings[n].coeff[2])
		c2 = str(self.swept_settings[n].coeff[3])
		c3 = str(self.swept_settings[n].coeff[4])
		c4 = str(self.swept_settings[n].coeff[5])
		c5 = str(self.swept_settings[n].coeff[6])

		rad_server  = self.swept_settings[n].rad_server
		rad_device  = self.swept_settings[n].rad_device
		rad_setting = self.swept_settings[n].rad_setting

		self.swp_inp_label.setText(label)
		self.swp_dd_type.setCurrentIndex(_type)
		self.swp_dd_vds.setCurrentIndex(-1)
		self.swp_dd_builtins.setCurrentIndex(builtin)
		self.swp_inp_vds_name.setText(vds_name)
		self.swp_inp_vds_id.setText(vds_id)

		self.swp_dd_rad_server.setCurrentIndex(rad_server)
		self.swp_dd_rad_device.setCurrentIndex(rad_device)
		self.swp_dd_rad_setting.setCurrentIndex(rad_setting)

		self.swp_inp_coeff_const.setText(cc)
		self.swp_inp_coeff_0.setText(c0)
		self.swp_inp_coeff_1.setText(c1)
		self.swp_inp_coeff_2.setText(c2)
		self.swp_inp_coeff_3.setText(c3)
		self.swp_inp_coeff_4.setText(c4)
		self.swp_inp_coeff_5.setText(c5)

		self.vis_swp(True)
		self.update_swept_setting_type()
	def update_swept_vds_data(self):
		c = self.vds_swp[self.swp_dd_vds.currentIndex()]
		self.swp_inp_vds_name.setText(c[1])
		self.swp_inp_vds_id.setText(c[0])
	def update_swept_setting_name(self,name):
		if self.swp_list_settings.currentRow() == -1:return
		self.swp_list_settings.currentItem().setText(name)
	def update_swept_setting_type(self):
		"""Enables/disables input regions based on selected setting type"""
		t = str(self.swp_dd_type.currentText())
		self.vis_swp_labrad(t=='LabRAD')
		self.vis_swp_vds(t=='VDS')
		self.vis_swp_builtin(t=='Builtin')
	def update_swept_setting_data(self):
		n = self.swp_list_settings.currentRow()
		if n == -1:return
		
		if str(self.swp_inp_label.text()) != "":self.swept_settings[n].label = str(self.swp_inp_label.text())
		self.swept_settings[n].type         = str(self.swp_dd_type.currentText())
		self.swept_settings[n].builtin_type = str(self.swp_dd_builtins.currentText())
		self.swept_settings[n].vds_name     = str(self.swp_inp_vds_name.text())
		self.swept_settings[n].vds_id       = str(self.swp_inp_vds_id.text())
		self.swept_settings[n].vds_dd       = str(self.swp_dd_vds.currentText())
		self.swept_settings[n].rad_server   = self.swp_dd_rad_server.currentIndex()
		self.swept_settings[n].rad_device   = self.swp_dd_rad_device.currentIndex()
		self.swept_settings[n].rad_setting  = self.swp_dd_rad_setting.currentIndex()
		self.swept_settings[n].coeff        = [str(self.swp_inp_coeff_const.text()),str(self.swp_inp_coeff_0.text()),str(self.swp_inp_coeff_1.text()),str(self.swp_inp_coeff_2.text()),str(self.swp_inp_coeff_3.text()),str(self.swp_inp_coeff_4.text()),str(self.swp_inp_coeff_5.text())]
		self.swept_settings[n].rad_inputs   = [str(self.swept_labrad_inputs[k].inp_value.text()) for k in range(self.swept_settings[n].rad_input_count)]
		self.swept_settings[n].rad_sweep_slot = self.get_labrad_sweep_slot()
	def get_labrad_sweep_slot(self):
		n=0
		for bar in self.swept_labrad_inputs:
			if bar.cb_sweep.isChecked():return n
			n+=1
		return None
	def update_swp_rad_dds(self):
		s = str(self.swp_dd_rad_server.currentText())
		
		# blank the device and setting fields
		self.swp_dd_rad_device.clear()
		self.swp_dd_rad_setting.clear()
		if s == '':return

		# add the devices for the selected server
		if len(self.devices[s]) == 0:
			print("Warning: selected server has no devices")
		else:
			self.swp_dd_rad_device.addItems([d[1] for d in self.devices[s]])

		# add the settings for the selected server
		if len(self.settings[s][0]) == 0:
			print("Warnign: selected server has no sweepable settings")
		else:
			self.swp_dd_rad_setting.addItems(self.settings[s][0])

		self.swp_dd_rad_device.setCurrentIndex(-1)
		self.swp_dd_rad_setting.setCurrentIndex(-1)

	def update_swp_rad_inputs(self,index):
		n=self.swp_list_settings.currentIndex()
		if n == -1:return
		server  = str(self.swp_dd_rad_server.currentText())
		setting = str(self.swp_dd_rad_setting.currentText())

		if len(setting)==0:
			self.swp_input_table.set_inputs([])
			return

		setting = self._cxn.servers[server].settings[setting]




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
		for widget in widgets:widget.setEnabled(vis)
	def vis_swp(self,vis):
		self.set_vis([
			self.swp_inp_label,
			self.swp_lbl_type,
			self.swp_dd_type,
			self.swp_lbl_coeff,
			self.swp_lbl_coeff_const,self.swp_inp_coeff_const,
			self.swp_lbl_coeff_0,self.swp_inp_coeff_0,
			self.swp_lbl_coeff_1,self.swp_inp_coeff_1,
			self.swp_lbl_coeff_2,self.swp_inp_coeff_2,
			self.swp_lbl_coeff_3,self.swp_inp_coeff_3,
			self.swp_lbl_coeff_4,self.swp_inp_coeff_4,
			self.swp_lbl_coeff_5,self.swp_inp_coeff_5,
			],vis)
		self.vis_swp_builtin(vis)
		self.vis_swp_labrad(vis)
		self.vis_swp_vds(vis)
	def vis_swp_labrad(self,vis):
		self.set_vis([
			self.swp_lbl_rad,
			#self.swp_lbl_rad_inp_name,
			#self.swp_lbl_rad_inp_units,
			#self.swp_lbl_rad_inp_value,
			#self.swp_lbl_rad_inp_sweep,
			self.swp_lbl_rad_input_req,
			self.swp_btn_rad_set_inputs,
			self.swp_lbl_rad_server,
			self.swp_lbl_rad_device,
			self.swp_lbl_rad_setting,
			self.swp_dd_rad_server,
			self.swp_dd_rad_device,
			self.swp_dd_rad_setting,
			],vis)
	def vis_swp_vds(self,vis):
		self.set_vis([
			self.swp_lbl_vds,
			self.swp_lbl_vds_name,
			self.swp_lbl_vds_id,
			self.swp_dd_vds,
			self.swp_inp_vds_name,
			self.swp_inp_vds_id,
			],vis)
	def vis_swp_builtin(self,vis):
		self.set_vis([
			self.swp_lbl_builtins,
			self.swp_dd_builtins,
			],vis)
	def vis_rec(self,vis):
		self.set_vis([
			self.rec_inp_label,
			self.rec_lbl_type,
			self.rec_dd_type,
			self.rec_lbl_ignore,
			self.rec_cb_ignore_0,self.rec_cb_ignore_1,self.rec_cb_ignore_2,
			self.rec_cb_ignore_3,self.rec_cb_ignore_4,self.rec_cb_ignore_5,
			self.rec_btn_ignore_all,
			],vis)
		self.vis_rec_labrad(vis)
		self.vis_rec_vds(vis)
		self.vis_rec_builtin(vis)
	def vis_rec_labrad(self,vis):
		self.set_vis([
			self.rec_lbl_rad,
			#self.rec_lbl_rad_inp_name,
			#self.rec_lbl_rad_inp_units,
			#self.rec_lbl_rad_inp_value,
			self.rec_lbl_rad_input_req,
			self.rec_btn_rad_set_inputs,
			self.rec_lbl_rad_server,
			self.rec_lbl_rad_device,
			self.rec_lbl_rad_setting,
			self.rec_dd_rad_server,
			self.rec_dd_rad_device,
			self.rec_dd_rad_setting,
			],vis)
	def vis_rec_vds(self,vis):
		self.set_vis([
			self.rec_lbl_vds,
			self.rec_lbl_vds_name,
			self.rec_lbl_vds_id,
			self.rec_dd_vds,
			self.rec_inp_vds_name,
			self.rec_inp_vds_id,
			],vis)
	def vis_rec_builtin(self,vis):
		self.set_vis([
			self.rec_lbl_builtins,
			self.rec_dd_builtins,
			],vis)

if __name__=='__main__':
	app = gui.QApplication(sys.argv)
	i = SetupWindow()
	i.show()
	sys.exit(app.exec_())
