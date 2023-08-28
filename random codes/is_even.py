
def is_even(num):
	lst = ["0","2","4","6","8"]
	feed = False
	for i in lst:
		if str(num).endswith(i):
			feed = True
	return feed
print(is_even(10))