import os, sys


class Scan():

	def __init__(self, path):

		self._all_files = os.scandir(path)
		self.lst = []

	def _loader(self):
		for i in self._all_files:
			# self.randnum = random.randint(0, len(self._all_files)-1)
			# self._extract = self._all_files[int(self.randnum)]
			if i.path.endswith(".mp3") and i.is_file:
				song = i.path
				try:
					self.lst.append(song)
					# print(i.path)
				except Exception as e:
					continue
			else:
				continue
			# break
		try:
			return self.lst
			print(sys.getsizeof(self.lst))
		except Exception as e:
			str_error = str(e).split()
			if ("'song'" in str_error): # and (self.num == 0)
				return "mp3"
			else:
				return False

if __name__ == '__main__':
	s = Scan("C:\\Users\\code\\Music")
	sfile = s._loader()
	print(sfile)
	print(sys.getsizeof(sfile))