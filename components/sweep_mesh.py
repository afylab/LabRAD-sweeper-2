import numpy

class Axis(object):
	def __init__(self,start,end,points,min_ramp_duration=None,post_ramp_delay=None):
		if points < 2:raise ValueError("Axis points (number of positions) must be at least 2. An axis of length 1 has no variation.")
		self.start  = start
		self.end    = end
		self.rng    = start-end
		self.points = points
		self.min_ramp_duration = min_ramp_duration if min_ramp_duration else 0.0
		self.post_ramp_delay   = post_ramp_delay   if post_ramp_delay   else 0.0

		self.values = numpy.linspace(start, end     , points)
		self.coords = numpy.linspace(0    , points-1, points).astype(int)

class SweepMesh(object):
	def __init__(self):
		self.has_mesh = False
		self.m        = numpy.array([])
		self.complete = False
		self.steps_done     = 0

		self.first_pos = True

	def total_steps(self):
		p=1
		for l in self.axis_lengths:
			p*=l
		return p-1

	def from_array(self,array):
		"""Takes mesh from an arbitrary array"""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		self.m              = array
		self.n_axes         = len(self.m.shape[:-1])
		self.axis_lengths   = [int(self.m.shape[n]) for n in range(self.n_axes)]
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.end_positions  = [length - 1 for length in self.axis_lengths]
		self.has_mesh       = True

	def from_functions(self,axes,functions):
		"""mesh[x,y,z,...][n] = functions[n](x,y,z,...)"""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		n_axes       = len(axes)
		n_functions  = len(functions)
		axis_lengths = [axis.points for axis in axes]
		self.m       = numpy.zeros(axis_lengths+[n_functions])
		for inst in range(n_functions):
			func = lambda *x:functions[inst]( *[axes[k].values[x[k].astype(int)] for k in range(len(x))] )
			self.m[...,inst::n_functions]=numpy.fromfunction(func,axis_lengths).reshape(axis_lengths+[1])

		self.n_axes         = n_axes
		self.axis_lengths   = axis_lengths
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.end_positions  = [length - 1 for length in self.axis_lengths]
		self.has_mesh       = True

	def from_linear_functions(self,axes,lincombs):
		"""mesh[x,y,z,...][n] = lincombs[n][0] + x*lincombs[n][1] + y*lincombs[n][2] + ..."""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		n_combs      = len(lincombs)
		n_axes       = len(axes)
		axis_lengths = [axis.points for axis in axes]
		self.m       = numpy.zeros(axis_lengths+[n_combs])
		for inst in range(n_combs):
			func = lambda *x:lincombs[inst][0]+sum([lincombs[inst][k+1]*axes[k].values[x[k].astype(int)] for k in range(n_axes)])
			self.m[...,inst::n_combs]=numpy.fromfunction(func,axis_lengths).reshape(axis_lengths+[1])

		self.n_axes         = n_axes
		self.axis_lengths   = axis_lengths
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.end_positions  = [length - 1 for length in self.axis_lengths]
		self.has_mesh       = True

	def next(self):
		"""Advances the position(s), then returns [(positions),(values),axis being stepped]. First call returns the origin of the mesh."""
		if not self.has_mesh: raise ValueError("mesh has not been generated yet")
		if self.complete    : raise ValueError("SweepMesh object has finished iterating")

		if self.first_pos:
			# We want the first next() call to return the values at (0,0,0,...) so we don't advance on the first call.
			self.first_pos = False
			return [list(self.axis_positions),numpy.array(tuple(self.m[tuple(self.axis_positions)])),-1]

		axis = 0
		done = False
		while not done:
			self.axis_positions[axis] += 1
			if self.axis_positions[axis] >= self.axis_lengths[axis]:
				self.axis_positions[axis]=0
				axis+=1
				if axis >= self.n_axes:
					self.complete=True
					done=True
			else:
				done = True
				if self.axis_positions == self.end_positions:
					self.complete = True

		self.steps_done += 1
		return [list(self.axis_positions),numpy.array(tuple(self.m[tuple(self.axis_positions)])),axis]

# examples
if __name__ == '__main__':
	f = SweepMesh()
	a1 = Axis(0,1,2)
	a2 = Axis(0,8,2)
	x     = lambda x,y:x
	y     = lambda x,y:y
	func1 = lambda x,y:x*y
	func2 = lambda x,y:x+y
	f.from_functions([a1,a2],[x,y,func1,func2])
	for inst in range(4):print(f.next())
	print("")

	g = SweepMesh()
	a1 = Axis(0,3,3)
	a2 = Axis(0,8,2)
	g.from_linear_functions([a1,a2],[ [1,0,0],[0,0,1],[0,1,0],[0,1,1] ])
	for inst in range(6):print(g.next())
	print("")

	a = SweepMesh()
	a.from_array(numpy.random.random_integers(0,7,[2,2,4]))
	for inst in range(4):print(a.next())
