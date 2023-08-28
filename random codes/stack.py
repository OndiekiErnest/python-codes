"""Avoiding amortized time bound 
    by using singly linked list as the underlying storage"""

class Stack:
    """LIFO Python empty stack"""
    #-------------Nested class------------------
    class _Node:
        """Nonpublic singly linked list class"""

        __slots__ = "_element", "_next" # --> streamline memory usage
        def __init__(self, element, nxt):
            self._element = element
            self._next = nxt
    #------------------------------------------

    def __init__(self):
        self._head = None
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        """ Return True if stack is empty"""
        return self._size == 0


    def top(self):
        """ Returns the top element of the stack (last added)"""
        if self.is_empty():
            raise Exception("Stack is empty")
        return self._head._element
        

    def push(self, e):
        """Add element e on top of the stack"""
        self._head = self._Node(e, self._head)
        self._size +=1

    def pop(self):
        """Pop the top element of the stack"""
        if self.is_empty():
            raise Exception("Stack is empty")
        value = self._head._element
        self._head = self._head._next
        self._size -=1
        return value
        


"""Running in amortized time bound"""
class Stacka:
    """LIFO Python stack of length n"""
    def __init__(self):
        self._data = [] # --> nonpublic instance

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        """ Return True if stack is empty"""
        return len(self._data) == 0

    def top(self):
        """ Returns the top element of the stack"""
        if self.is_empty():
            raise Exception("Stack is empty")
        return self._data[-1]

    def push(self, e):
        """Add element e on top of the stack"""
        self._data.append(e)

    def pop(self):
        """Pop the top element of the stack"""
        if self.is_empty():
            raise Exception("Stack is empty")
        return self._data.pop()

r = Stack()
