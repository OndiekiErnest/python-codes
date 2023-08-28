def reverse(self):
	if len(self) <= 1:
		return self
	else:
		return reverse(self[1:]) +self[0]
		

user = input('Enter string to reverse: ')
print(reverse(user))


def reverse_list(elem):
	if len(elem) <= 1:
		return elem
	else:
		return reverse_list(elem[1:]) + [elem[0]]


lst = [1,2,3,4,5,6,7,'slim','thick']
print(reverse_list(lst))