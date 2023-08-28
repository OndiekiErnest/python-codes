"""Runs in amortized time bound O(1)* """

class Queue:
	"""FIFO implementation using list as storage"""
	CAPACITY = 10
	def __init__(self):
		self._data = [0]*CAPACITY
		self._size = 0
		self._front = 0


	def __len__(self):
		return self._size

	def _resize(self, cap):
		"""Resize to a new list of capacity >= len(self)"""
		old = self._data
		self._data = [None]*cap
		walk = self._front
		for i in range(self._size):
			self._data[i] = old[walk]
			walk = (walk+1) % len(old)
		self._front = 0
	def is_empty(self):
		"""Returns True if queue is empty"""
		return self._size == 0

	def first(self):
		"""Returns the first element of the queue without removing it

		Raise an exception if queue is empty"""
		if self.is_empty():
			raise Exception("Queue is empty")
		return self._data[self._front]

	def enqueue(self, e):
		"""Adds element to the back of the queue"""
		if self._size == len(self._data):
			self.resize(2 * len(self._data))
		avail = (self._size + self._front) % len(self._data)
		self._data[avail] = e
		self._size +=1

	def dequeue(self):
		"""Removes and returns the first element of the queue

		Raise error if queue is empty"""
		if self.is_empty():
			raise Exception("Queue is empty")
		answer = self._data[self._front]
		self._data[self._front] = None # --> Help garbage collection
		self._front = (self._front+1) % len(self._data)
		self._size -=1
		if 0 < self._size < len(self._data) // 4: # --> shrinks the list by half
						self._resize(len(self._data) // 2)
		return answer
"""Runs in constant time O(1)"""

class QueueL:
	"""FIFO queue implementation using a singly linked list for storage"""

	#-------------------------Nested class---------------------------
	class _Node:
		"""Nonpublic class for singly linked list"""
		__slots__ = "_element","_next"
		def __init__(self, element, nxt):
			self._element = element
			self._next = nxt

	#----------------------------------------------------------------
	def __init__(self):
		self._head = None
		self._tail = None
		self._size = 0

	def __len__(self):
		return self._size

	def is_empty(self):
		"""Return True if queue is empty"""
		return self._size == 0

	def first(self):
		"""Only returns the top element"""
		if self.is_empty():
			raise Exception("Queue is empty")
		return self._head._element

	def enqueue(self, e):
		"""Add element e at the back of queue"""
		newest = self._Node(e, None)
		if self.is_empty():
			self._head = newest
		else:
			self._tail._next = newest
		self._tail = newest
		self._size +=1

	def dequeue(self):
		"""Removes and returns the top element"""
		if self.is_empty():
			raise Exception("Queue is empty")
		answer = self._head._element
		self._head = self._head._next
		self._size -=1
		if self.is_empty():
			self._tail = None # --> Removed head had been the tail
		return answer
q =QueueL()
