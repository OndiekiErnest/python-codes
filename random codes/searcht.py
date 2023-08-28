import os, re

class Search:
	"""Search("keywords","path")
	loops through files in a directory 
	
	performs search through keywords
	"""

	def __init__(self, string, folder = os.path.dirname(os.path.abspath(__file__))):
		self._string = set(string.lower().split())
		self._path = folder


	def lookup(self):
		"""return file if there's a match
		
		else return false
		""" 
		for f in os.listdir(self._path):
			file = f
			f = f.replace("_"," ").replace("-"," ").replace("."," ").lower()
			keywords = set(f.split())
			if len(keywords.intersection(self._string)) == len(self._string):
					yield os.path.join(self._path, file)
		else:
			yield False

			#-----------runs in double the time the above takes for small outputs---------
			# srch = re.compile(r"[\w]+")
			# rslt = srch.findall(f)
			# if set(rslt).intersection(self._string) != set():
			# 	yield file
if __name__ == "__main__":
	for i in Search("vivian","C:\\Users\\code\\Music").lookup():
		print(i)
