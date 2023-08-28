
def each_sum(num = input("Enter integer: ")):
	total = 0
	try:
		num = int(num)
		while num > 0:
			last = num%10
			total +=last
			num //= 10
		return total
	except Exception as e:
		print(e)
print(each_sum())

