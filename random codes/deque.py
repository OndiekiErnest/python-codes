class _DLBASE:
	"""Base class to implement doubly linked class"""
	class _Node:
		"""For storing doubly linked node"""
		__slots__ = "_element", "_prev", "_next"
		def __init__(self, elem, prev, nxt):
			self._element = elem
			self._prev = prev
			self._next = nxt

	def __init__(self):
		self._header = self._Node(None,None,None)
		self._trailer = self._Node(None,None,None)
		self._header._next = self._trailer
		self._trailer._prev = self._header
		self._size = 0

	def __len__(self):
		return self._size

	def _is_empty(self):
		return self._size == 0

	def _insert_btn(self,e,pre,s):
		"""Insert in between two nodes"""
		newest = self._Node(e,pre,s)
		pre._next = newest
		s._prev = newest
		self._size +=1
		return newest

	def _delete(self,node):
		"""Delete node"""
		pre = node._prev
		s = node._next
		pre._next = s
		s._prev = pre
		self._size -=1
		elem = node._element	
		node._prev = node._next = node._element = None
		return elem


class Deque(_DLBASE):
	"""Double-ended queue"""
	def first(self):
		"""Only returns element at the front"""
		if self._is_empty():
			raise Exception("Deque is empty")
		return self._header._next._element

	def last(self):
		"""Only returns element at the back"""
		if self._is_empty():
			raise Exception("Deque is empty")
		return self._trailer._prev._element

	def insert_first(self,e):
		"""Insert in front"""
		self._insert_btn(e,self._header,self._header._next)

	def insert_last(self,e):
		"""Insert at the back"""
		self._insert_btn(e,self._trailer._prev,self._trailer)

	def delete_first(self):
		"""Remove and return front element"""
		if self._is_empty():
			raise Exception("Deque is empty")
		return self._delete(self._header._next)

	def delete_last(self):
		"""Remove and return back element"""
		if self._is_empty():
			raise Exception("Deque is empty")
		return self._delete(self._trailer._prev)
