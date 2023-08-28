def minmax(lst):
	largest = lst[-1]
	smallest = lst[0]
	for i in lst:
		if i < smallest:
			smallest = i
		elif i > largest:
			largest = i
	return smallest, largest
	
from random import randint as r


print(minmax([0,1,2,3,7,4,10,5,6,7,8,9]))
