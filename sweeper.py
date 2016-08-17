from components.sweep_mesh import SweepMesh
from components.settings   import SettingObject

class Sweeper(object):
	def __init__(self):
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

