import time

builtins = {
	'get':['time','zero'],
	'set':['do nothing'],
}

class Setting(object):
	def __init__(self,connection=None,max_ramp_speed=None,label=None):
		self.connection     = connection
		self.max_ramp_speed = max_ramp_speed
		if max_ramp_speed is not None:
			if max_ramp_speed <= 0:raise ValueError("max_ramp_speed cannot be zero (or less than zero)")

		self.label   = label if label else None
		self.kind    = None  # what kind of setting this is. 'vds' or 'dev' or 'builtin'
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

	def getlabel(self):
		return self.label

	def set_max_ramp_speed(self,max_ramp_speed):
		if max_ramp_speed is not None:
			if max_ramp_speed <= 0:raise ValueError("max_ramp_speed cannot be zero (or less than zero)")
		self.max_ramp_speed = max_ramp_speed

	def connect(self,connection):
		"""Supplies a LabRAD connection to the Setting. Not necessary if one was supplied on init."""
		if self.connected:raise ValueError("Already connected")

		self.connection = connection
		self.connected  = True

		if self.has_setting:
			self.setting.connect(connection)

			if self.label is None:
				# label detection for 'vds' kind
				if self.kind == 'vds':
					self.label=self.setting.details[2] if self.setting.details[2] else None
					if self.label == None:raise ValueError("Label has not been specified by user or by VDS")

				# label detection for 'dev' kind
				if self.kind == 'dev':
					self.label = self.setting.setting[2]

				# label detection for 'builtin' kind
				if self.kind == 'builtin':
					self.label = self.setting.which

			self.ready = True

	def vds(self,ID,name=None):
		"""Connects to a channel from the VDS."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = VDSSetting(ID,name)
		self.kind        = 'vds'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)

			if self.label is None:
				self.label=self.setting.details[2] if self.setting.details[2] else None
				if self.label == None:raise ValueError("Label has not been specified by user or by VDS")

			self.ready = True

	def dev_get(self,setting,inputs):
		"""Connects to a <get> setting from a LabRAD Device Server."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = DeviceGetSetting(setting,inputs)
		self.kind        = 'dev'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)

			if self.label is None:
				self.label = self.setting.setting[2]
				
			self.ready = True

	def dev_set(self,setting,inputs,var_slot):
		"""Connectes to a <set> setting from a LabRAD Device Server."""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting     = DeviceSetSetting(setting,inputs,var_slot)
		self.kind        = 'dev'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)
			if self.label is None:
				self.label = self.setting.setting[2]
			self.ready = True

	def builtin(self,which):
		"""Connects to a builtin setting"""
		if self.has_setting:raise ValueError("Setting already defined")

		self.setting = BuiltinSetting(which)

		self.kind = 'builtin'
		self.has_setting = True

		if self.connected:
			self.setting.connect(self.connection)
			if self.label is None:
				self.label = self.setting.which
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

class BuiltinSetting(object):
	def __init__(self,which):
		if not (which in builtins['get'] + builtins['set']):
			raise ValueError

		self.which = which

		if which in builtins['get']:
			self.has_get = True
			self.has_set = False

		if which in builtins['set']:
			self.has_get = False
			self.has_set = True

	def connect(self,connection):
		"""No connection is needed for builtin settings. This may change, in which case the connection should be saved as an internal property."""
		pass

	def get(self):
		if not self.has_get:
			raise ValueError("Tried to perform 'get' on a 'set' type builtin")

		if self.which == 'zero':
			return 0.0

		if self.which == 'time':
			return time.time()

		raise ValueError("ERR: could not identify builtin setting <{which}>".format(which=self.which))

	def set(self,value):
		if not self.has_set:
			raise ValueError("Tried to perform 'set' on a 'get' type builtin")

		if self.which == 'do nothing':
			return

		raise ValueError("ERR: could not identify builtin setting <{which}>".format(which=self.which))

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

	s1 = Setting(c)  # connection can either be passed during init, or given later by the Setting.connect(connection) command
	s1.vds('3004')   # configure the Setting as a VDS channel
	print(s1.set(1)) # set values with .set(v)
	print(s1.get())  # get values with .get()
	print("")        # 'vds' settings can do both get and set, but only if the channel they've been given can get and set.

	s2 = Setting()   # Here we initialize without a connection
	s2.connect(c)    # So we need to give it a connection before using it
	s2.vds('','DC7') # configure the Setting as VDS channel (this time specifying name rahter than ID)
	print(s2.set(250))
	print("")

	s3 = Setting() # 
	s3.vds('3004') # note that we can perform configuration and connection in any order
	s3.connect(c)  # here we connect after configuring the Setting.
	print(s3.set(0.5))
	print("")

	s4 = Setting()
	s4.dev_set(['ad5764_dcbox','ad5764_dcbox (COM28)','set_voltage'],[3],1) # Here we configure the Setting as a device server setting of the "set" type
	s4.connect(c)
	print(s4.set(0.250))
	print("")

	s5 = Setting(c)
	s5.dev_get(['ad5764_dcbox','ad5764_dcbox (COM28)','get_voltage'],[3]) # Here we configure the Setting as a device server setting of the "get" type
	print(s5.get())
	print('')

	c.disconnect()
