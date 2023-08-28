def is_multiple(n, m):
	value = False
	if n%m == 0:
		value = True
	return value
		
print(is_multiple(16, 3))