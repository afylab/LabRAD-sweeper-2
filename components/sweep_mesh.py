import numpy

class SweepMesh(object):
	def __init__(self):
		self.has_mesh = False
		self.mesh     = numpy.array([])
		self.complete = False

	def from_array(self,array):
		"""Takes mesh from an arbitrary array"""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		self.mesh           = array
		self.n_axes         = len(self.mesh.shape[:-1])
		self.axis_lengths   = [int(self.mesh.shape[n]) for n in range(self.n_axes)]
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.has_mesh       = True

	def from_functions(self,axis_lengths,functions):
		"""mesh[x,y,z,...][n] = functions[n](x,y,z,...)"""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		n_axes      = len(axis_lengths)
		n_functions = len(functions)
		self.mesh   = numpy.zeros(axis_lengths+[n_functions])
		for inst in range(n_functions):
			self.mesh[...,inst::n_functions]=numpy.fromfunction(functions[inst],axis_lengths).reshape(axis_lengths+[1])

		self.n_axes         = n_axes
		self.axis_lengths   = axis_lengths
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.has_mesh       = True

	def generate(self,axis_lengths,lincombs):
		"""mesh[x,y,z,...][n] = lincombs[n][0] + x*lincombs[n][1] + y*lincombs[n][2] + ..."""
		if self.has_mesh:raise ValueError("Mesh already generated/loaded")
		n_combs   = len(lincombs)
		n_axes    = len(axis_lengths)
		self.mesh = numpy.zeros(axis_lengths+[n_combs])
		for inst in range(n_combs):
			func = lambda *axes:lincombs[inst][0]+sum([lincombs[inst][n+1]*axes[n] for n in range(n_axes)])
			self.mesh[...,inst::n_combs]=numpy.fromfunction(func,axis_lengths).reshape(axis_lengths+[1])

		self.n_axes         = n_axes
		self.axis_lengths   = axis_lengths
		self.axis_positions = [0 for n in range(self.n_axes)]
		self.has_mesh       = True

	def next(self):
		"""Returns [(positions),(values)] then advances the position(s)"""
		if not self.has_mesh: raise ValueError("mesh has not been generated yet")
		if self.complete    : raise ValueError("SweepMesh object has finished iterating")
		ret  = [tuple(self.axis_positions),tuple(self.mesh[tuple(self.axis_positions)])]
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
		return ret

# examples
if __name__ == '__main__':
	l = SweepMesh()
	l.from_lincombs([2,3],[ [0.0,1.0,2.0], [1.0,0.5,0.5], [0.0,0.0,0.0] ])
	for inst in range(6):print(l.next())
	print('')

	f = SweepMesh()
	func1 = lambda x,y:(3*x + y + 1)
	func2 = lambda x,y:x*y
	f.from_functions([2,2],[func1,func2])
	for inst in range(4):print(f.next())
	print('')

	a = SweepMesh()
	a.from_array(numpy.random.random_integers(0,7,[2,2,4]))
	for inst in range(4):print(a.next())
