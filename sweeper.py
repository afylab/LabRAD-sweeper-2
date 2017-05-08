from components.sweep_mesh import SweepMesh, Axis
from components.settings   import Setting
from components.logger     import DataSet
import labrad, time

class Sweeper(object):
	def __init__(self):
		self._cxn  = labrad.connect()
		self._mesh = SweepMesh() # starts not generated. Can be generated once all axes / settings are defined.
		self._axes = []          # list of axes (just stored as their lengths.)
		self._swp  = []          # list of settings (SettingObject instances) to be set each step
		self._rec  = []          # list of settings (SettingObject instances) to be recorded each step
		self._axes_labels = []   # list of axis labels

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

	# Read-only access functions. Note that while it is possible to modify the objects returned, it is discouraged.
	def axes(self):
		return tuple(self._axes)
	def swp(self):
		return tuple(self._swp)
	def rec(self):
		return tuple(self._rec)

	# setup mode functions
	def add_axis(self,start,end,points,min_ramp_duration=None,post_ramp_delay=None,label=None):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._axes.append(Axis(start,end,points,min_ramp_duration,post_ramp_delay))
		self._axes_labels.append("" if label is None else label)

	def add_swept_setting(self, kind, label=None, max_ramp_speed=None, ID=None, name=None, setting=None, inputs=None, var_slot=None, which_builtin=None):
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

		'max_ramp_speed' is the maximum speed (in input value / second) at which the setting will be changed.
		This will limit the speed at which the sweep will take place. If it is set to None, there will be no
		limit enforced for this setting; if all swept settings have None for max_ramp_speed, there will be no
		limit enforced at all.
		"""
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")

		if kind == 'vds':
			if not ((setting is None) and (inputs is None) and (var_slot is None)):
				print("Warning: specified at least one of setting,inputs,var_slot for a 'vds' type setting. These are properties for a 'dev' type setting, and will be ignored.")
			if not (which_builtin is None):
				print("Warning: specified which_builtin for a 'vds' type setting. This property is for 'builtin' type settings, and will be ignored.")
			
			s = Setting(self._cxn,max_ramp_speed=max_ramp_speed)
			s.vds(ID,name)      # Since a connection has been passed, this will error if ID/name don't point to a valid channel.
			                    # So, no need to check for that here.
			
			if not s.setting.has_set:raise ValueError("Specified VDS channel does not have a 'set' command and therefore cannot be swept.")
			
			self._swp.append(s) # This will only be called if no error is thrown (so the setting is guaranteed to be valid)

		elif kind == 'dev':
			if (setting is None) or (inputs is None) or (var_slot is None):
				raise ValueError("For a 'dev' type setting: setting, inputs, and var_slot must be specified.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'dev' type setting. These are properties for the 'vds' type setting, and will be ignored.")
			if not (which_builtin is None):
				print("Warning: specified which_builtin for a 'dev' type setting. This property is for 'builtin' type settings, and will be ignored.")
			
			s = Setting(self._cxn,max_ramp_speed=max_ramp_speed,label=label)
			s.dev_set(setting,inputs,var_slot)
			self._swp.append(s)

		elif kind == 'builtin':
			if which_builtin is None:
				raise ValueError("For a 'builtin' type setting, which_builtin must be specified")
			if not ((setting is None) and (inputs is None) and (var_slot is None)):
				print("Warning: specified at least one of setting,inputs,var_slot for a 'builtin' type setting. These are properties for a 'dev' type setting, and will be ignored.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'builtin' type setting. These are properties for the 'vds' type setting, and will be ignored.")

			s = Setting(self._cxn,max_ramp_speed=max_ramp_speed,label=label)
			s.builtin(which_builtin)
			if s.setting.has_set is False:
				raise ValueError("Cannot use builtin <{which_builtin}> as swept setting; it is a get-only builtin".format(which_builtin=which_builtin))
			self._swp.append(s)

		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting) or 'builtin' (for a builtin setting). Got {kind} instead.".format(kind=kind))

	def add_recorded_setting(self, kind, label=None, ID=None, name=None, setting=None, inputs=None, which_builtin=None):
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
			if not (which_builtin is None):
				print("Warning: specified which_builtin for a 'vds' type setting. This property is for 'builtin' type settings, and will be ignored.")
			
			s = Setting(self._cxn)
			s.vds(ID,name)      # Since a connection has been passed, this will error if ID/name don't point to a valid channel.
			                    # So, no need to check for that here.
			
			if not s.setting.has_get:raise ValueError("Specified VDS channel does not have a 'get' command and therefore cannot be recorded.")
			
			self._rec.append(s) # This will only be called if no error is thrown (so the setting is guaranteed to be valid)

		elif kind == 'dev':
			if (setting is None) or (inputs is None):
				raise ValueError("For a 'dev' type setting: setting and inputs must be specified.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'dev' type setting. These are properties for the 'vds' type setting, and will be ignored.")
			if not (which_builtin is None):
				print("Warning: specified which_builtin for a 'dev' type setting. This property is for 'builtin' type settings, and will be ignored.")

			s = Setting(self._cxn,label=label)
			s.dev_get(setting,inputs)
			self._rec.append(s)

		elif kind == 'builtin':
			if which_builtin is None:
				raise ValueError("For a 'builtin' type setting, which_builtin must be specified")
			if not ((setting is None) and (inputs is None)):
				print("Warning: specified at least one of setting,inputs,var_slot for a 'builtin' type setting. These are properties for a 'dev' type setting, and will be ignored.")
			if not ((name is None) and (ID is None)):
				print("Warning: specified name and/or ID for a 'builtin' type setting. These are properties for the 'vds' type setting, and will be ignored.")

			s = Setting(self._cxn,label=label)
			s.builtin(which_builtin)
			if s.setting.has_get is False:
				raise ValueError("Cannot use builtin <{which_builtin}> as recorded setting; it is a set-only builtin".format(which_builtin=which_builtin))
			self._rec.append(s)


		else:
			raise ValueError("'kind' must be 'vds' (for a Virtual Device Server setting) or 'dev' (for a LabRAD Device Server setting) or 'builtin' (for a builtin setting). Got {kind} instead.".format(kind=kind))

	def clear_axes(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._axes=[]
	def clear_swept_settings(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._swp=[]
	def clear_recorded_settings(self):
		if self._mode != 'setup':raise ValueError("This function is only available in setup mode")
		self._rec=[]

	def generate_mesh(self,lincombs,do_pre_sweep=False,do_post_sweep=False,start_rampfrom=None,end_rampto=None):
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

		self._mesh.from_linear_functions(self._axes,lincombs)
		self._lincombs = lincombs
		self._mode = 'sweep'

		self._do_pre_sweep   = do_pre_sweep
		self._do_post_sweep  = do_post_sweep
		self._start_rampfrom = start_rampfrom
		self._end_rampto     = end_rampto

		self._configure_sweep()

	# sweep mode functions
	def _configure_sweep(self):
		"""This function is called automatically when the mesh is generated. It configures the properties & objects necessary to begin sweeping."""
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")

		# DataSet object (self._dataset) creation
		axis_parameter = [ ["axis_details"       , '**i', [ [axis.start,axis.end,axis.points,axis.min_ramp_duration,axis.post_ramp_delay] for axis in self._axes     ]] ] # start value, end value, and number of points for each axis
		comb_parameter = [ ["linear_combinations", '**v', [ [float(c) for c in comb]                                                      for comb in self._lincombs ]] ] # linear combinations for each swept setting

		comments = [
			["Created by LabRAD-Sweeper-2","computer"],
			]

		axis_pos_indep = [ ['axis_{n}_pos'.format(n=n),'i'] for n in range(len(self._axes)) ] # independent variables representing the positions for each axis
		axis_val_indep = [ ['axis_{n}_val'.format(n=n),'v'] for n in range(len(self._axes)) ] # independent variables representing the values    for each axis
		settings_indep = [ [setting.getlabel()                   ,'v'] for setting in self._swp        ] # independent variables representing the values    for each swept    setting
		dependents     = [ [setting.getlabel(),setting.getlabel(),'v'] for setting in self._rec        ] # dependent   variables representing the values    for each recorded setting

		self._dataset = DataSet(           # we don't include the name & location yet so that the user can choose when to specify them.
			axis_pos_indep+settings_indep, # independent variables. For now we don't include the axis_val_indeps
			dependents,                    # dependent   variables.
			)
		self._dataset.add_comments(comments)
		self._dataset.add_parameters(axis_parameter+comb_parameter)



		# internal sweep properties
		self._ds_ready   = False # whether or not the dataset has been initialized (and is ready to be written to)
		self._speedlimit = any([setting.max_ramp_speed is not None for setting in self._swp]) # whether or not any setting has a speed limitation
		
		self._axes_loc, self._targ_state, axis = self._mesh.next()
		# _axes_loc   : set of integer positions along each axis
		# _targ_state : the state (list of swept setting values) that the next measurement will be taken.

		if self._do_pre_sweep:
			self._sweep_phase = 'pre_sweep'
			self._pre_sweep_progress = 0.0
			self._pre_sweep_duration = 0.0

			for n in range(len(self._swp)):
				if self._swp[n].max_ramp_speed is not None:
					self._pre_sweep_duration = max([self._pre_sweep_duration, abs(self._targ_state[n]-self._start_rampfrom[n])/self._swp[n].max_ramp_speed])
			
			if self._pre_sweep_duration == 0.0:
				self._do_pre_sweep = False
				#If the pre-sweep isn't constrained by ramp rates, it can be done in one step. This is best achieved by simply not doing a pre-sweep.

		if not (self._do_pre_sweep):
			self._sweep_phase = 'sweep'
			self._ramp_cycle = 'delay' # start in the delay cycle so that the first measurement is preceeded by an interval with unchanging settings
			self._delay_duration = self._axes[0].post_ramp_delay*0.001 if self._axes[0].post_ramp_delay else 0.0
			self._delay_progress = 0.0
			self._set_state(self._targ_state)

		#self._last_state = None # the state (list of swept setting values) that the last measurement was taken at. For the first measurement it's None.
		#self._progress   = 0.0  # progress (0 -> 1) from last state to target state
		#self._duration   = 0.0  # duration of current step in seconds. Zero for first state.

	def initialize_dataset(self,dataset_name,dataset_location):
		"""Ininitializes the dataset & makes it ready to take data/comments/parameters. Name and location must both be specified at this time."""
		if self._mode == 'setup': raise ValueError("This function is only usable after the sweep has been started. It can still be used after the sweep is complete.")
		if self._ds_ready       : raise ValueError("Dataset has already been initialized")

		# process location
		while dataset_location.startswith('\\'):
			dataset_location=dataset_location[1:]
		while dataset_location.endswith('\\'):
			dataset_location=dataset_location[:-1]
		location = ['']+dataset_location.replace('\\','\n').splitlines()

		self._dataset.set_name(dataset_name)
		self._dataset.set_location(location)
		self._dataset.create_dataset()

		self._ds_ready = True
		self._dataset.write_data()
		self._dataset.write_parameters()
		self._dataset.write_comments()

		if self._mode == 'done':
			self.close()

	def add_comments(self,comments):
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")
		self._dataset.add_comments(comments,self._ds_ready)
	def add_parameters(self,parameters):
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")
		self._dataset.add_parameters(parameters,self._ds_ready)
	def has_speedlimit(self):
		return bool(self._speedlimit)
	def done(self):
		return bool(self._mode == 'done')


	def _set_state(self,state):
		"""Sets the state of each swept setting. This should not be called except by the Sweeper class itself."""
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")

		if len(state) != len(self._swp):
			raise ValueError("Length of state must equal number of swept settings")
		for n in range(len(self._swp)):
			self._swp[n].set(state[n])

	def _do_measurement(self,output=False):
		"""Takes a measurement and advances the mesh. This should not be called except by the Sweeper class itself."""
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")

		if output:print("measurement at {_targ_state}".format(_targ_state=self._targ_state))
		measurements = [setting.get() for setting in self._rec]
		self._dataset.add_data([ self._axes_loc + list(self._targ_state) + measurements ],self._ds_ready)

		self._last_state = self._targ_state.copy()
		if not self._mesh.complete:
			self._axes_loc, self._targ_state, next_axis_step = self._mesh.next()
		else:
			if self._do_post_sweep:
				self._sweep_phase = 'post_sweep'
				self._post_sweep_progress = 0.0
				self._post_sweep_duration = 0.0
				for n in range(len(self._swp)):
					if self._swep[n].max_ramp_speed is not None:
						self._post_sweep_duration = max([self._post_sweep_duration, abs(self._end_rampto[n]-self._targ_state[n])/self._swp[n].max_ramp_speed])


			else:
				self._terminate_sweep()

			return

		# reset _progress, calculate new _duration
		if self._speedlimit:
			self._ramp_progress = 0.0
			self._delay_progress = 0.0

			self._ramp_cycle = 'ramp'
			self._ramp_duration = 0.0
			for n in range(len(self._swp)):
				if self._swp[n].max_ramp_speed is not None:
					self._ramp_duration = max([self._ramp_duration, abs(self._targ_state[n]-self._last_state[n])/self._swp[n].max_ramp_speed])
			self._ramp_duration = max([self._ramp_duration,self._axes[next_axis_step].min_ramp_duration*0.001]) # Minimum delay set by axis delay (in milliseconds)

			self._delay_duration = self._axes[next_axis_step].post_ramp_delay * 0.001

	def advance(self,time_elapsed,output=False):
		if self._mode != 'sweep': raise ValueError("This function is only usable in sweep mode")
		if not self._speedlimit : raise ValueError("Cannot advance by time elapsed without speed limit (no swept setting has a speed limit enforced.) To advance the sweep, please use Sweeper.step()")
		if time_elapsed <= 0    : raise ValueError("time_elapsed must be greater than zero")

		if self._sweep_phase == 'pre_sweep':
			self._pre_sweep_progress += time_elapsed / self._pre_sweep_duration
			self._pre_sweep_progress = min([self._pre_sweep_progress,1.0])
			self._set_state(self._targ_state*self._pre_sweep_progress + self._start_rampfrom*(1-self._pre_sweep_progress))

			if self._pre_sweep_progress >= 1.0:
				self._sweep_phase = 'sweep'
				self._ramp_cycle = 'delay' # start in the delay cycle so that the first measurement is preceeded by an interval with unchanging settings
				self._delay_duration = self._axes[0].post_ramp_delay if self._axes[0].post_ramp_delay else 0.0
				self._delay_progress = 0.0

		elif self._sweep_phase == 'sweep':

			if self._ramp_cycle == 'delay':
				self._delay_progress += time_elapsed / self._delay_duration if self._delay_duration else 1.0
				if self._delay_progress >= 1.0:
					print('doing measurement')
					self._do_measurement()
					print('')

			elif self._ramp_cycle == 'ramp':
				self._ramp_progress += time_elapsed / self._ramp_duration if self._ramp_duration else 1.0
				self._ramp_progress = min([self._ramp_progress,1.0])
				self._set_state(self._targ_state*self._ramp_progress + self._last_state*(1-self._ramp_progress))
				if self._ramp_progress >= 1.0:
					print('ramp done, starting delay')
					self._ramp_cycle = 'delay'
					self._delay_progress = 0.0

		elif self._sweep_phase == 'post_sweep':
			self._post_sweep_progress += time_elapsed / self._post_sweep_duration if self._post_sweep_duration else 1.0
			self._post_sweep_progress = min([self._post_sweep_progress,1.0])
			self._set_state(self._end_rampto*self._post_sweep_progress + self._targ_state*(1-self._post_sweep_progress))
			if self._post_sweep_progress >= 1.0:
				self._terminate_sweep()


	def step(self,stepsize=0.1):
		"""
		Performs one step in the sweep.

		If there is no speed limit, this simply performs the next measurement.
		Once the target state has been reached, a measurement will be taken, recorded, and the next target will be set.

		If there is a speed limit, this ramps at the appropriate speed until it gets to the target state.
		Delay between steps will be equal to stepsize (0.1 seconds by default), enforced with time.sleep()
		In general this is only the right way to perform the sweep if it is being performed in the Python Shell.
		If this is the case then the best way would be to call Sweeper.autosweep(), which will call step() until
		the end of the mesh is reached.

		Timing the sweep with time.sleep() is not always reliable, and so the best way to use the Sweeper is to
		have it managed by a program that keeps its own internal time (such as a PyQt application,) and using the
		advance(time_elapsed) method with accurate timing.
		"""
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")

		if self._speedlimit:
			
			while self._progress < 1:

				timeleft = (1-self._progress) * self._duration
				
				if timeleft > stepsize:
					time.sleep(stepsize)
					self.advance(stepsize)

				else:
					time.sleep(timeleft)
					self._do_measurement
					break
		else:
			# no speed limit
			self._do_measurement()

	def autosweep(self,stepsize=0.1,output=False):
		while self._mode == 'sweep':
			if output:
				print("Performing step at axes position {axes} and state {state}".format(axes=self._axes_loc,state=list(self._targ_state)))
			self.step(stepsize)
			

	def _terminate_sweep(self):
		if self._mode != 'sweep':raise ValueError("This function is only usable in sweep mode")
		self._mode = 'done'
		print("Sweep completed.")
		if not (self._ds_ready):
			print("Warning: although the sweep has been completed, the dataset has not been created yet (and so the data has not been recorded.) To create the dataset, use Sweeper.initalize_dataset(name,location) and the data will be written automatically.")
		else:
			self.close()

	def close(self):
		print("Sweep and log completed, closing LabRAD Connections")
		self._cxn.disconnect()
		self._dataset.close_dataset()
		print("Connections closed.")

# example usage
if __name__ == '__main__':

	s = Sweeper()
	s.add_axis(0,1,11)
	s.add_swept_setting(    'dev', label="SET QUAD 0", setting=['dcbox_quad_ad5780','dcbox_quad_ad5780 (COM20)','set_voltage'],inputs=[0],var_slot=1)
	s.add_swept_setting(    'dev', label="SET QUAD 1", setting=['dcbox_quad_ad5780','dcbox_quad_ad5780 (COM20)','set_voltage'],inputs=[1],var_slot=1)
	s.add_recorded_setting( 'dev', label="GET QUAD 0", setting=['dcbox_quad_ad5780','dcbox_quad_ad5780 (COM20)','get_voltage'],inputs=[0])
	s.add_recorded_setting( 'dev', label="GET QUAD 1", setting=['dcbox_quad_ad5780','dcbox_quad_ad5780 (COM20)','get_voltage'],inputs=[1])
	s.generate_mesh([[0,1],[0,2]])

	s.autosweep(output=True)

	# s.initalize_dataset('ds_test_3','\\data\\test\\')
	# ^
	# |
	# this would create the appropriate data set. It's commented out to prevent unnecessary files.
	# the dataset initializeation can be called ay any point before during or after the sweep.
	# Before it is called, all data (and comments, and parameters) are stored but not written
	# When it is called, all stored data (and comments, and parametrs) will be written
	# Once is has been called, all data and comments and parameteres are written as they are acquired.
