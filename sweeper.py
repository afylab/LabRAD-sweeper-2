from components.sweep_mesh import SweepMesh, Axis
from components.settings   import Setting
from components.logger     import DataSet
import labrad

class Sweeper(object):
	def __init__(self):
		self._cxn  = labrad.connect()
		self._mesh = SweepMesh() # start not generated. Can be generated once all axes / settings are defines.
		self._axes = []          # list of axes (just stored as their lengths.) <self.mesh.mesh.shape> will be <self.axes + [len(self.swp)]>
		self._swp  = []          # list of settings (SettingObject instances) to be set each step
		self._rec  = []          # list of settings (SettingObject instances) to be recorded each step

		self._mode  = 'setup'    # Current mode/status of the Sweeper object.
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
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._axes.append(Axis(start,end,points))

	def add_swept_setting(self, kind, label=None, ID=None, name=None, setting=None, inputs=None, var_slot=None):
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

		'label' is the axis label that this setting will take, as well as its name in the data vault file.
		If it is not specified, it takes the default value of the setting name for 'dev' settings, or the
		label specified in the registry for 'vds' settings. For 'vds' settings, if no label is specified
		in the registry, the label MUST be specified here.
		"""
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")

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
			
			s = Setting(self._cxn,label=label)
			s.dev_set(setting,inpts,var_slot)
			self._swp.append(s)

		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting). Got {kind} instead.".format(kind=kind))

	def add_recorded_setting(self, kind, label=None, ID=None, name=None, setting=None, inpts=None):
		"""
		Adds a setting to be recorded.
		kind is either 'vds' for a Virtual Device Server setting,
		or 'dev' for a regular LabRAD Device Server setting.

		In the case of kind='vds', specify:
		name and/or ID to determine the VDS channel.

		In the case of kind='dev', specify:
		setting = [server,device,setting],
		inputs  = all inputs to the setting

		'label' is the axis label that this setting will take, as well as its name in the data vault file.
		If it is not specified, it takes the default value of the setting name for 'dev' settings, or the
		label specified in the registry for 'vds' settings. For 'vds' settings, if no label is specified
		in the registry, the label MUST be specified here.
		"""
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")

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
			
			e = setting(self._cxn,label=label)
			s.dev_get(setting,inputs)
			self._swp.append(s)

		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting). Got {kind} instead.".format(kind=kind))

	def clear_axes(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._axes=[]
	def clear_swept_settings(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._swp=[]
	def clear_recorded_settings(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._rec=[]

	def generate_mesh(self,lincombs):
		"""
		Generates the mesh from linear combinations of the axes.
		One linear combination is required for each swept setting,
		in the order in which the swept settings were added.

		The form of a linear combination is:
		[constant, coeff_0, coeff_1, ...]
		It starts with a constant offset term, and has one
		additional coefficient for each axis present.
		"""
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		if len(lincombs) != len(self._swp):
			raise ValueError("Must specify exactly one linear combination (set of coefficients) per swept setting. Number of swept settings is {_swp}".format(_swp=len(self._swp)))
		for comb in lincombs:
			if len(comb) != 1 + len(self._axes):
				raise ValueError("Length of a linear combination must be (1 + number_of_axes); one constant term plus a coefficient for each axis. Expected length: {len1}, got length {len2} from linear combination {comb}".format(len1=len(self._axes)+1,len2=len(comb),comb=comb))
			comb = [float(c) for c in comb] # ensure that values in each combination are valid as floats

		self._mesh.generate(self._axes,lincombs)
		self._lincombs = lincombs
		self._mode = 'sweep'
		self._configure_sweep()

	# sweep mode functions
	def _configure_sweep(self):
		"""This function is called automatically when the mesh is generated. It configures the properties & objects necessary to begin sweeping."""
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")

		# DataSet object (self._dataset) creation
		axis_parameter = [ ["axis_details",        [ [axis.start,axis.end,axis.points] for axis in self._axes     ]] ] # start value, end value, and number of points for each axis
		comb_parameter = [ ["linear_combinations", [ [float(c) for c in comb]          for comb in self._lincombs ]] ] # linear combinations for each swept setting

		comments = [
			["Created by LabRAD-Sweeper-2","computer"],
			]

		axis_pos_indep = [ ['axis_{n}_pos'.format(n=n),'i'] for n in range(len(self._axes)) ] # independent variables representing the positions for each axis
		axis_val_indep = [ ['axis_{n}_val'.format(n=n),'v'] for n in range(len(self._axes)) ] # independent variables representing the values    for each axis
		settings_indep = [ [setting.label()           ,'v'] for setting in self._swp        ] # independent variables representing the values    for each swept    setting
		dependents     = [ [setting.label()           ,'v'] for setting in self._rec        ] # dependent   variables representing the values    for each recorded setting

		self._dataset = DataSet(           # we don't include the name & location yet so that the user can choose when to specify them.
			axis_pos_indep+settings_indep, # independent variables. For now we don't include the axis_val_indeps
			dependents,                    # dependent   variables.
			)

		# internal sweep properties
		# ...

	def initalize_dataset(self,dataset_name,dataset_location):
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")
		self._dataset.set_name(dataset_name)
		self._dataset.set_location(dataset_location)
		self._dataset.create_dataset()