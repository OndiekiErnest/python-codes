from functools import lru_cache
from sys import setrecursionlimit

setrecursionlimit(2000)
@lru_cache(maxsize=2000)
def fib(n):
	"""Implementing implicit cache (lru_cache): 
		Returns Fibbonaci of n"""
	if n == 1 or n == 2:
		return 1
	elif n == 0:
		return 0
	elif n > 2:
		return fib(n-1) + fib(n-2)

#for i in range(1001):
#	print(i,":",fib(i),"\n\n")
	
cache = {}
def fibb(n):
	"""Implementing explicit cache:
		Returns Fibbonaci of n"""
	if n in cache:
		return cache[n]
	elif n == 1 or n == 2:
		value = 1
	elif n == 0:
		value = 0
	else:
		value = fibb(n-2) + fibb(n-1)
	cache[n] = value
	return value

#for i in range(1000):
#	print(i,":",fibb(i),"\n\n")
