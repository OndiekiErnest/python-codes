import string, random
import re as r

class Password:
	def __init__(self):
		self.char = string.ascii_letters + string.digits + string.punctuation
		self.strength = r.compile(r"[\d\w\s]")

	def generate(self, length=8):
		self.length = length
		self.key = [random.choice(self.char) for i in range(self.length)]
		return ''.join(self.key)
r = Password()
print(r.generate(12))




