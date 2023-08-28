from random import randint
def shuffle(lst):
	new = []
	for i in lst:
		elem = lst[randint(0, len(lst)-1)]
		if elem not in new: new.append(elem)
	if len(new) != len(lst):
		for i in lst:
			if i not in new: new.append(i)
	return new

print(shuffle(["Good","morning","six"]))
