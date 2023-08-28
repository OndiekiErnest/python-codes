class _DLBASE:
    """Base class to implement doubly linked class"""
    class _Node:
        """For storing doubly linked node"""
        __slots__ = "element_", "prev", "next_"

        def __init__(self, elem, prev, nxt):
            self.element_ = elem
            self.prev = prev
            self.next_ = nxt

    def __init__(self):
        self._header = self._Node(None, None, None)
        self._trailer = self._Node(None, None, None)
        self._header.next_ = self._trailer
        self._trailer.prev = self._header
        self._size = 0

    def __len__(self):
        return self._size

    def _is_empty(self):
        return self._size == 0

    def _insert_btn(self, e, pre, s):
        """Insert in between two nodes"""
        newest = self._Node(e, pre, s)
        pre.next_ = newest
        s.prev = newest
        self._size += 1
        return newest

    def _delete(self, node):
        """Delete node"""
        pre = node.prev
        s = node.next_
        pre.next_ = s
        s.prev = pre
        self._size -= 1
        elem = node.element_
        node.prev = node.next_ = node.element_ = None
        return elem


class Deque(_DLBASE):
    """Double-ended queue"""

    def first(self):
        """Only returns element at the front"""
        if self._is_empty():
            raise Exception("Deque is empty")
        return self._header

    def last(self):
        """Only returns element at the back"""
        if self._is_empty():
            raise Exception("Deque is empty")
        return self._trailer.prev

    def insert_first(self, e):
        """Insert in front"""
        self._insert_btn(e, self._header, self._header.next_)

    def insert_last(self, e):
        """Insert at the back"""
        self._insert_btn(e, self._trailer.prev, self._trailer)

    def delete_first(self):
        """Remove and return front element"""
        if self._is_empty():
            raise Exception("Deque is empty")
        return self._delete(self._header.next_)

    def delete_last(self):
        """Remove and return back element"""
        if self._is_empty():
            raise Exception("Deque is empty")
        return self._delete(self._trailer.prev)
