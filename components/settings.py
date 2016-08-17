class Setting(object):
	def __init__(self,connection=None):
		self.connection = connection

		self.kind    = None  # what kind of setting this is. 'vds' or 'dev'
		self.setting = None  # the setting object (instance of VDSSetting, DeviceGetSetting, or DeviceSetSetting.)
		                     # These classes have common menthods called by the Setting class.

		self.connected   = not (connection is None) # Whether or not the Setting has been given a connection
		self.has_setting = False                    # Whether or not the Setting has been given a setting
		self.ready       = False                    # Whether or not the Setting has been completed.

	def get(self):
		if not self.ready:raise ValueError("Not ready to do get/set. Please ensure that the connection and setting have both been added.")
		return self.setting.get()

	def set(self,value):
		if not self.ready:raise ValueError("Not ready to do get/set. Please ensure that the connection and setting have both been added.")
		return self.setting.set(value)

	def connect(self,connection):
		"""Supplies a LabRAD connection to the Setting. Not necessary if one was supplied on init."""
		if self.connected:raise ValueError("Already connected")

		self.connection = connection
		self.connected  = True

		if self.has_setting:
			self.setting.connect(connection)
			self.ready = True

	def vds(self,ID,name=None):
		"""Connects to a channel from the VDS."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = VDSSetting(ID,name)
		self.kind        = 'vds'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)
			self.ready = True

	def dev_get(self,setting,inputs):
		"""Connects to a <get> setting from a LabRAD Device Server."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = DeviceGetSetting(setting,inputs)
		self.kind        = 'dev'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)
			self.ready = True

	def dev_set(self,setting,inputs,var_slot):
		"""Connectes to a <set> setting from a LabRAD Device Server."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = DeviceSetSetting(setting,inputs,var_slot)
		self.kind        = 'dev'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)
			self.ready = True




class VDSSetting(object):
	def __init__(self,ID,name=None):
		self.connection = None
		self.connected  = False

		self.has_get = None # These start off unknown (None)
		self.has_set = None # They will be determined upon connecting

		self.ID   = ID   if ID   else ""
		self.name = name if name else ""

	def connect(self,connection):
		# Ensure that the connection is valid and that the VDS is running
		self.details    = connection.virtual_device_server.list_channel_details(self.ID,self.name)
		self.has_get    = self.details[5]
		self.has_set    = self.details[6]
		
		self.connection = connection
		self.connected  = True

	def get(self):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		if not self.has_get  : raise ValueError("Setting does not support get")
		return self.connection.virtual_device_server.get_channel(self.ID,self.name)

	def set(self,value):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		if not self.has_set  : raise ValueError("Setting does not support set")
		return self.connection.virtual_device_server.set_channel(value,self.ID,self.name)

class DeviceGetSetting(object):
	def __init__(self,setting,inputs):
		self.setting = setting
		self.inputs  = inputs
		self.ctx     = None

		self.has_get = True
		self.has_set = False

	def connect(self,connection):

		# ensure that the connection is valid, and the server & device are present.
		self.ctx = connection.context()
		connection.servers[self.setting[0]].select_device(self.setting[1],context=self.ctx)

		self.connection = connection
		self.connected  = True

	def get(self):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		try:
			resp = self.connection.servers[self.setting[0]].settings[self.setting[2]](*self.inputs,context=self.ctx)
			return resp
		except:
			self.connection.servers[self.setting[0]].select_device(self.setting[1],context=self.ctx)
			resp = self.connection.servers[self.setting[0]].settings[self.setting[2]](*self.inputs,context=self.ctx)
			return resp

	def set(self):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		raise ValueError("Setting does not support set")

class DeviceSetSetting(object):
	def __init__(self,setting,inputs,var_slot):
		if var_slot > len(inputs):raise ValueError("var_slot cannot exceed number of non-variable inputs")

		self.setting  = setting
		self.inputs   = inputs
		self.var_slot = var_slot
		self.ctx      = None

		self.has_get = False
		self.has_set = True

	def connect(self,connection):

		# ensure that the connection is valid, and the server & device are present.
		self.ctx = connection.context()
		connection.servers[self.setting[0]].select_device(self.setting[1],context=self.ctx)

		self.connection = connection
		self.connected  = True

	def get(self):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		raise ValueError("Setting does not support get")

	def set(self,value):
		if not self.connected: raise ValueError("Setting not yet connected to LabRAD")
		inp = self.inputs[:self.var_slot] + [value] + self.inputs[self.var_slot:]
		try:
			resp = self.connection.servers[self.setting[0]].settings[self.setting[2]](*inp,context=self.ctx)
			return resp
		except:
			self.connection.servers[self.setting[0]].select_device(self.setting[1],context=self.ctx)
			resp = self.connection.servers[self.setting[0]].settings[self.setting[2]](*inp,context=self.ctx)
			return resp

# examples
if __name__ == '__main__':
	import labrad
	c = labrad.connect()

	s1 = Setting(c)
	s1.vds('3004')
	print(s1.set(1))
	print(s1.get())
	print("")

	s2 = Setting()
	s2.connect(c)
	s2.vds('','DC7')
	print(s2.set(250))
	print("")

	s3 = Setting()
	s3.vds('3004')
	s3.connect(c)
	print(s3.set(0.5))
	print("")

	s4 = Setting()
	s4.dev_set(['ad5764_dcbox','ad5764_dcbox (COM28)','set_voltage'],[3],1)
	s4.connect(c)
	print(s4.set(0.250))
	print("")

	s5 = Setting(c)
	s5.dev_get(['ad5764_dcbox','ad5764_dcbox (COM28)','get_voltage'],[3])
	print(s5.get())
	print('')

	c.disconnect()
