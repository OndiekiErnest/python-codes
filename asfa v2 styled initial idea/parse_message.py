"""
parse messages for server and client
Author: Ernesto
"""

class Parser():
    __slots__ = "_msg"
    def __init__(self, msg: str):
        self._msg = msg

    def parse(self)-> tuple:
        """
            Useful in getting the sender
            return (sender, message)
        """
        if len(self._msg) > 1:
            split_txt = self._msg.split()
            sender = "".join(split_txt[0])
            txt = " ".join(split_txt[1:])
            return sender, txt.strip()
    
    def parse_replied(self) -> tuple:
        """
            Useful in formatting reply texts
            return (replied_text, message)
        """
        if len(self._msg) > 1:
            sliced_txt = self._msg[self._msg.index("(")+1: self._msg.index(")")]
            if len(sliced_txt) > 37:
                msg = f'{sliced_txt[:34]}...'
            else:
                msg = f'{sliced_txt}'
            return msg.encode(), self._msg[self._msg.index(")")+2:].encode()
    
