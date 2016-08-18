from components.sweep_mesh import SweepMesh, Axis
from components.settings   import Setting
import labrad

class Sweeper(object):
	def __init__(self):
		self._cxn  = labrad.connect()
		self._mesh = SweepMesh() # start not generated. Can be generated once all axes / settings are defines.
		self._axes = []          # list of axes (just stored as their lengths.) <self.mesh.mesh.shape> will be <self.axes + [len(self.swp)]>
		self._swp  = []          # list of settings (SettingObject instances) to be set each step
		self._rec  = []          # list of settings (SettingObject instances) to be recorded each step

		self.mode  = 'setup'     # Current mode/status of the Sweeper object.
		                         # setup = currently setting up for the sweep. Not ready to set/take data.
		                         #         This is the only mode where axes, settings, etc. can be modified.
		                         #         This mode is ended when the mesh is generated.
		                         #
		                         # sweep = data collection ready/underway. This mode is entered upon generating the mesh.
		                         #         In this mode, settings are swept and recorded, data is logged, and the mesh is advanced.
		                         #         This mode ends once the last mesh.next() state has been finished (swept, recorded, logged.)
		                         #
		                         # done  = data collection finished. No more settings will be called (set or recorded), nor data logged.
		                         #         In this mode, the Sweeper object is inert; it cannot do anything.
		                         #         Its properties can still be accessed / read, however.

	# Read-only access functions
	def axes(self):
		return tuple(self._axes)
	def swp(self):
		return tuple(self._swp)
	def rec(self):
		return tuple(self._rec)

	# setup mode functions
	def add_axis(self,start,end,points):
		if not (self.mode == 'setup'):raise ValueError("add_axis function only available in setup mode")
		self._axes.append(Axis(start,end,points))

	def add_swept_setting(self, kind, ID=None, name=None, setting=None, inputs=None, var_slot=None):
		"""
		Adds a setting to be swept.
		kind is either 'vds' for a Virtual Device Server setting,
		or 'dev' for a regular LabRAD Device Server setting.

		In the case of kind='vds', specify:
		name and/or ID to determine the VDS channel.

		In the case of kind='dev', specify:
		setting  = [server,device,setting],
		inputs   = all non-varied inputs to the setting,
		var_slot = what position the varied input is put in.
		"""
		if kind == 'vds':
			if not ((setting is None) and (inputs is None) and (var_slot is None)):
				print("Warning: specified at least one of setting,inptus,var_slot for a 'vds' type setting. These are properties for a 'dev' type setting, and will be ignored.")
			
			s = Setting(self._cxn)
			s.vds(ID,name)      # Since a connection has been passed, this will error if ID/name don't point to a valid channel.
			                    # So, no need to check for that here.
			
			if not s.has_set:raise ValueError("Specified VDS channel does not have a 'set' command and therefore cannot be swept.")
			
			self._swp.append(s) # This will only be called if no error is thrown (so the setting is guaranteed to be valid)

		elif kind == 'dev':
			if (setting is None) or (inputs is None) or (var_slot is None):
				raise ValueError("For a 'dev' type setting: setting, inpts, and var_slot must be specified.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'dev' type setting. These are properties for the 'vds' type setting, and will be ignored.")
			
			s = Setting(self._cxn)
			s.dev_set(setting,inpts,var_slot)
			self._swp.append(s)

		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting). Got {kind} instead.".format(kind=kind))

	def add_recorded_setting(self, kind, ID=None, name=None, setting=None, inpts=None):
		"""
		Adds a setting to be recorded.
		kind is either 'vds' for a Virtual Device Server setting,
		or 'dev' for a regular LabRAD Device Server setting.

		In the case of kind='vds', specify:
		name and/or ID to determine the VDS channel.

		In the case of kind='dev', specify:
		setting = [server,device,setting],
		inputs  = all inputs to the setting
		"""
		if kind == 'vds':
			if not ((setting is None) and (inputs is None)):
				print("Warning: specified at least one of setting,inptus for a 'vds' type setting. These are properties for a 'dev' type setting, and will be ignored.")
			
			s = Setting(self._cxn)
			s.vds(ID,name)      # Since a connection has been passed, this will error if ID/name don't point to a valid channel.
			                    # So, no need to check for that here.
			
			if not s.has_get:raise ValueError("Specified VDS channel does not have a 'get' command and therefore cannot be recorded.")
			
			self._swp.append(s) # This will only be called if no error is thrown (so the setting is guaranteed to be valid)

		elif kind == 'dev':
			if (setting is None) or (inputs is None):
				raise ValueError("For a 'dev' type setting: setting and inputs must be specified.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'dev' type setting. These are properties for the 'vds' type setting, and will be ignored.")
			
			e = setting(self._cxn)
			s.dev_get(setting,inputs)
			self._swp.append(s)

		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting). Got {kind} instead.".format(kind=kind))








	# setup -> sweep
	# generate mesh
	# pass connection to settings


