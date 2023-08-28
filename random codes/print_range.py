def nrange(start,stop=None,step=1):
	"""prints upto n-1 like the range()"""
	if stop is None:
		stop = start
		start = 0
	if start < stop:
		print(start)
		start += step
		nrange(start,stop,step)
	return

print(nrange(11))

def ntuple(n):
	"""Returns  a tuple of n-1 elements"""
	if n < 1:
		return ()
	return ntuple(n-1) + (n-1,)
		
print(ntuple(11))
