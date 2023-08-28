from random import randint, randrange, choice
def typos(s):
	reps = ['a','i','e','o','u']
	values = {randrange(0,10,2) for i in range(4)}
	for i in range(11):
		if i in values:
			num = randint(0, len(s)-1)
			if s[num] != " ":
				snt = s.replace(s[num], reps[randint(0, len(reps)-1)])
				print(snt)
			else:
				pass
			
typos("A good morning to you Bammy and your sister.")
