
def product(m, n):
        
	"""
                Return product by addition of m, n
                Works if any of the parameters is below recursion limit
        """
	
	if n == 0 or m == 0:
		return 0
	if m > n:
		return product(m, n-1)+m
	else:
		return product(m-1, n)+n
		
print(product(992, 19037120773))
