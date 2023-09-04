from PyQt6.QtWidgets import (
    QPushButton, QStyleOptionButton,
    QStylePainter, QStyle,
)
from PyQt6.QtCore import (
    Qt, QRect, QSize,
)
from PyQt6.QtGui import QIcon


class Button(QPushButton):
    """ custom QPushButton widget """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SideBarButton(Button):
    """ custom button which sets icon top and text bottom """

    __slots__ = ("_icon", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._icon = self.icon()
        if not self._icon.isNull():
            super().setIcon(QIcon())

    def sizeHint(self):
        hint = super().sizeHint()
        if not self.text() or self._icon.isNull():
            return hint
        style = self.style()
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        margin = style.pixelMetric(style.PixelMetric.PM_ButtonMargin, opt, self)
        spacing = style.pixelMetric(style.PixelMetric.PM_LayoutVerticalSpacing, opt, self)
        # get the possible rect required for the current label
        labelRect = self.fontMetrics().boundingRect(
            0, 0, 5000, 5000, Qt.TextFlag.TextShowMnemonic, self.text())
        iconHeight = self.iconSize().height()
        height = iconHeight + spacing + labelRect.height() + margin * 2
        if height > hint.height():
            hint.setHeight(height)
        return hint

    def setIcon(self, icon):
        # setting an icon might change the horizontal hint, so we need to use a
        # "local" reference for the actual icon and go on by letting Qt to *think*
        # that it doesn't have an icon;
        if icon == self._icon:
            return
        self._icon = icon
        self.updateGeometry()

    def paintEvent(self, event):
        if self._icon.isNull() or not self.text():
            super().paintEvent(event)
            return
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        opt.text = ''
        qp = QStylePainter(self)
        # draw the button without any text or icon
        qp.drawControl(QStyle.ControlElement.CE_PushButton, opt)

        rect = self.rect()
        style = self.style()
        margin = style.pixelMetric(style.PixelMetric.PM_ButtonMargin, opt, self)
        iconSize = self.iconSize()
        iconRect = QRect(int((rect.width() - iconSize.width()) / 2), margin,
                         iconSize.width(), iconSize.height())
        if self.underMouse():
            state = QIcon.Mode.Active
        elif self.isEnabled():
            state = QIcon.Mode.Normal
        else:
            state = QIcon.Mode.Disabled
        qp.drawPixmap(iconRect, self._icon.pixmap(iconSize, state))

        spacing = style.pixelMetric(style.PixelMetric.PM_LayoutVerticalSpacing, opt, self)
        labelRect = QRect(rect)
        labelRect.setTop(iconRect.bottom() + spacing)
        qp.drawText(labelRect,
                    Qt.TextFlag.TextShowMnemonic | Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    self.text())


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("QPushButton {font-size: 18px; background: gray; border 2px solid gray; border-radius: 5px; }")
    w = SideBarButton('This is an error icon', icon=QIcon("data\\error.png"))
    w.setIconSize(QSize(32, 32))
    w.show()
    sys.exit(app.exec())
