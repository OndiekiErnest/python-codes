from PyQt6.QtWidgets import QFrame


class Line(QFrame):
    def __init__(self, h=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if h:
            # defaults to horizontal line
            self.setFrameShape(QFrame.Shape.HLine)
        else:
            self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
