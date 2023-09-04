""" Video player made using PyQt6 and VLC """

from PyQt6.QtWidgets import (
    QFrame,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QLabel,
    QStyle,
    QToolTip,
    QGroupBox,
    QComboBox,
    QStyleOptionSlider,
    QWidgetAction,
)
from PyQt6.QtCore import (
    Qt,
    QSize,
    QPoint,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QIcon,
)
from itertools import cycle
import os
# create and bind keyboard shortcuts

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")


def _icon(basename: str):
    """ return QIcon of basename """
    return QIcon(os.path.join(ICONS_DIR, basename))


class Slider(QSlider):
    """ custom slider with tool tip of slider value """

    _mouse_released = pyqtSignal(int)

    def __init__(self, *args, hide_timer=None, pop_offset=QPoint(0, -30), **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("slider")
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setRange(0, 100)
        self.setValue(50)
        self.setSingleStep(1)

        self.hide_timer = hide_timer
        self.opt = QStyleOptionSlider()

        self.valueChanged.connect(self.show_tip)

    def show_tip(self, value=None):
        """ popup to show value """
        # calculate offset
        pop_offset = QPoint(0, -int(self.height() * 2))

        self.initStyleOption(self.opt)
        rectHandle = self.style().subControlRect(QStyle.ComplexControl.CC_Slider,
                                                 self.opt, QStyle.SubControl.SC_SliderHandle,
                                                 self,
                                                 )

        pos_local = rectHandle.topLeft() + pop_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, str(self.value()), self)

    def pixelPosToRangeValue(self, pos):
        """ get value from position, in whichever style """
        self.initStyleOption(self.opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider,
                                         self.opt, QStyle.SubControl.SC_SliderGroove,
                                         self,
                                         )
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider,
                                         self.opt, QStyle.SubControl.SC_SliderHandle,
                                         self,
                                         )

        if self.orientation() == Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Orientation.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                              sliderMax - sliderMin, self.opt.upsideDown)

    def mousePressEvent(self, event):
        """ jump directly to where the mouse clicked """
        if event.button() == Qt.MouseButton.LeftButton:
            # event.accept()
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)
        return super().mousePressEvent(event)

    def enterEvent(self, event):
        if self.hide_timer:
            self.hide_timer.stop()
        # change cursor shape
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # show tip
        self.show_tip()
        # call super class
        return super().enterEvent(event)

    def mouseReleaseEvent(self, event):
        value = self.pixelPosToRangeValue(event.pos())
        self._mouse_released.emit(value)
        # show tip
        self.show_tip()
        # call super class
        return super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self.hide_timer:
            self.hide_timer.start()
        # change cursor shape
        self.setCursor(Qt.CursorShape.ArrowCursor)
        # call super class
        return super().leaveEvent(event)


class PointSlider(QSlider):
    """ custom slider for sliding point-level values """

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=1, *args, **kargs):

        self._multi = 10 ** decimals

        # init parent class
        super().__init__(*args, **kargs)
        self.setOrientation(Qt.Orientation.Horizontal)
        self.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.setTickInterval(2)

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super().value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self) -> float:
        return float(super().value()) / self._multi

    def setRange(self, mini: int, maxi: int):
        min_val = mini * self._multi
        max_val = maxi * self._multi
        return super().setRange(min_val, max_val)

    def setMinimum(self, value: int):
        return super().setMinimum(value * self._multi)

    def setMaximum(self, value: int):
        return super().setMaximum(value * self._multi)

    def setSingleStep(self, value: int):
        return super().setSingleStep(value * self._multi)

    def singleStep(self) -> float:
        return float(super().singleStep()) / self._multi

    def setValue(self, value: int):
        return super().setValue(int(value * self._multi))

    def leaveEvent(self, event):
        # change cursor shape
        self.setCursor(Qt.CursorShape.ArrowCursor)
        # call super class
        return super().leaveEvent(event)

    def enterEvent(self, event):
        # change cursor shape
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # call super class
        return super().enterEvent(event)


class PlaySpeedAction(QWidgetAction):
    """ widget to be treated as action """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slider_group = QGroupBox("Playback Speed")
        layout = QVBoxLayout(self.slider_group)

        self.slider = PointSlider()
        self.slider.setRange(2, 20)
        self.slider.setSingleStep(10)
        # add slider to layout
        layout.addWidget(self.slider)

        self.setDefaultWidget(self.slider_group)

    @property
    def value(self):
        """ get slider value """
        return self.slider.value()

    @value.setter
    def value(self, value: int):
        """ set slider value """
        self.slider.setValue(value)


class CtrlBtn(QPushButton):
    """" custom controls button """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(60)
        self.setIconSize(QSize(32, 32))


class LeFrame(QFrame):
    """ custom base frame that responds to leave/enter events """

    def __init__(self, *args, timer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("leframe")

        self.hide_timer = timer

    def enterEvent(self, event):
        if self.hide_timer:
            self.hide_timer.stop()

        return super().enterEvent(event)

    def leaveEvent(self, event):
        if self.hide_timer:
            self.hide_timer.start()

        return super().leaveEvent(event)


class HidingBtn(LeFrame):
    """" custom for a single btn that responds to leave/enter events """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, timer=hide_timer, **kwargs)

        self.btn = CtrlBtn()

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(self.btn)


class MultiStateBtn(CtrlBtn):
    """ base class for multi-state btns """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._icons = cycle(())

        self.clicked.connect(self.change_icon)

    def change_icon(self):
        self.setIcon(next(self._icons))


class MinMaximizeBtn(QPushButton):
    """ dual-state btn that switches btwn up and down arrows """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFixedHeight(32)

        self._icons = cycle((_icon("down.png"), _icon("up.png")))

        self.clicked.connect(self.change_icon)
        # initial icon setup
        self.change_icon()

    def change_icon(self):
        """ switch btwn icons endlessly """
        self.setIcon(next(self._icons))


class PlayPauseBtn(MultiStateBtn):
    """ custom play/pause btn """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("playbtn")

        self._icons = cycle((_icon("play.png"), _icon("pause.png")))
        # set icon
        self.change_icon()


class MuteBtn(MultiStateBtn):
    """ custom mute btn with changing states  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("mutebtn")

        self._icons = cycle((_icon("sound.png"), _icon("mute.png")))
        # set icon
        self.change_icon()


class RepeatBtn(MultiStateBtn):
    """ custom mute btn with changing states  """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("repeatbtn")

        self._icons = cycle(
            (_icon("repeatall.png"),
             _icon("repeatone.png"),
             _icon("order.png"),
             )
        )
        # set icon
        self.change_icon()


class SoundCtrls(LeFrame):
    """ custom QFrame holding sound control buttons """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, timer=hide_timer, **kwargs)
        self.setObjectName("soundctrls")

        self.hide_timer = hide_timer

        btns_layout = QHBoxLayout(self)
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns_layout.setSpacing(5)
        # btns
        self.mute_btn = MuteBtn()
        self.mute_btn.setCheckable(True)
        self.mute_btn.setChecked(False)
        # volume slider
        self.v_slider = Slider()
        self.v_slider.setFixedWidth(100)
        self.v_slider.hide()

        btns_layout.addWidget(self.mute_btn)
        btns_layout.addWidget(self.v_slider)
        # set max resize
        w = self.mute_btn.width() + self.v_slider.width() + 30
        self.setMaximumWidth(w)

    @property
    def volume(self) -> int:
        """ player volume """
        return self.v_slider.value()

    @volume.setter
    def volume(self, value: int):
        """ player volume """
        self.v_slider.setValue(value)

    def enterEvent(self, event):
        self.v_slider.show()

        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.v_slider.hide()

        return super().leaveEvent(event)


class MediaCtrls(LeFrame):
    """ custom QFrame for media control buttons """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, timer=hide_timer, **kwargs)
        self.setObjectName("mediactrls")

        self.hide_timer = hide_timer

        btns_layout = QHBoxLayout(self)
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns_layout.setSpacing(5)

        self.prev_btn = CtrlBtn()
        self.prev_btn.setIcon(_icon("prev.png"))
        self.play_pause_btn = PlayPauseBtn()
        self.next_btn = CtrlBtn()
        self.next_btn.setIcon(_icon("next.png"))

        btns_layout.addWidget(self.prev_btn)
        btns_layout.addWidget(self.play_pause_btn)
        btns_layout.addWidget(self.next_btn)

        w = self.prev_btn.width() + self.play_pause_btn.width() + self.next_btn.width() + 30
        self.setMaximumWidth(w)


class OrderCtrls(LeFrame):
    """ custom QFrame for play-order control buttons """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, timer=hide_timer, **kwargs)
        self.setObjectName("orderctrls")

        self.hide_timer = hide_timer

        btns_layout = QHBoxLayout(self)
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns_layout.setSpacing(5)

        # shuffle btn
        self.shuffle_btn = CtrlBtn()
        self.shuffle_btn.setIcon(_icon("shuffle.png"))
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setChecked(False)
        # repeat btn
        self.loop_btn = RepeatBtn()
        self.loop_btn.hide()

        btns_layout.addWidget(self.shuffle_btn)
        btns_layout.addWidget(self.loop_btn)

        w = self.loop_btn.width() + self.shuffle_btn.width() + 30
        self.setMaximumWidth(w)

    def enterEvent(self, event):
        self.loop_btn.show()

        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.loop_btn.hide()

        return super().leaveEvent(event)


class TracksCtrls(LeFrame):
    """ custom QFrame to hold buttons for choosing tracks """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, timer=hide_timer, **kwargs)
        self.setObjectName("tracksctrls")

        self.hide_timer = hide_timer

        btns_layout = QHBoxLayout(self)
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns_layout.setSpacing(5)

        # audio chooser
        self.audio_tracks = QComboBox()
        # subtitles chooser
        self.subtitles_list = QComboBox()
        self.subtitles_list.hide()

        btns_layout.addWidget(self.audio_tracks)
        btns_layout.addWidget(self.subtitles_list)

        w = self.subtitles_list.width() + self.audio_tracks.width() + 30
        self.setMaximumWidth(w)

    def add_audio_tracks(self, tracks):
        """ add list of audio tracks """
        self.audio_tracks.addItems(tracks)

    def add_subtitles(self, subs):
        """ add a list of subtitles """
        self.subtitles_list.addItems(subs)

    def get_current(self) -> tuple[str]:
        """ return the current audio track, and subtitle if available """
        current_audio = self.audio_tracks.currentText()
        current_sub = self.subtitles_list.currentText()
        # return strings
        return current_audio, current_sub

    def set_current(self, audio: str, sub: str):
        """ set current texts for audio and subs """
        self.audio_tracks.setCurrentText(audio)
        self.subtitles_list.setCurrentText(sub)

    def enterEvent(self, event):
        self.subtitles_list.show()

        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.subtitles_list.hide()

        return super().leaveEvent(event)


class VidWindow(QFrame):
    """ video display window """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("vidwin")
        self.setMouseTracking(True)  # so we can detect cursor move

        # palette = self.palette()
        # palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        # self.setPalette(palette)
        self.setAutoFillBackground(True)

        # is height reduced
        self.height_reduced = False

        self.main_layout = QVBoxLayout(self)

        self.top_layout = QHBoxLayout()
        side = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
        self.top_layout.setAlignment(side)

        self.ctrls_layout = QHBoxLayout()

        self.btns_timer = QTimer()
        self.btns_timer.setInterval(3000)  # ms
        self.btns_timer.timeout.connect(self.hide_ctrls)

        self.create_ctrls()
        # start timer on startup
        self.btns_timer.start()

    def create_ctrls(self):
        """ create control buttons """
        self.volume_label = QLabel("Volume: 100%")
        # btns
        self.minmaxbtn = MinMaximizeBtn()
        self.minmaxbtn.clicked.connect(self.reduce_height)
        self.snap_btn = HidingBtn(hide_timer=self.btns_timer)
        self.snap_btn.btn.setIcon(_icon("screenshot.png"))

        self.sound_ctrls = SoundCtrls(hide_timer=self.btns_timer)
        # bind signals
        self.sound_ctrls.v_slider.valueChanged.connect(self.update_vol_str)
        self.media_ctrls = MediaCtrls(hide_timer=self.btns_timer)
        self.order_ctrls = OrderCtrls(hide_timer=self.btns_timer)
        self.tracks_ctrls = TracksCtrls(hide_timer=self.btns_timer)
        self.tracks_ctrls.add_subtitles(("English", "Korea"))
        self.tracks_ctrls.add_audio_tracks(("English", "Korea"))
        # add to their layout
        left_side = Qt.AlignmentFlag.AlignLeft
        self.ctrls_layout.addWidget(self.snap_btn, alignment=left_side)
        self.ctrls_layout.addStretch()  #
        center_side = Qt.AlignmentFlag.AlignCenter
        self.ctrls_layout.addWidget(self.sound_ctrls, alignment=center_side)
        self.ctrls_layout.addWidget(self.media_ctrls, alignment=center_side)
        self.ctrls_layout.addWidget(self.order_ctrls, alignment=center_side)
        self.ctrls_layout.addStretch()  #
        # tracks_side = Qt.AlignmentFlag.AlignRight
        # self.ctrls_layout.addWidget(self.tracks_ctrls, alignment=tracks_side)

        self.progressbar = Slider(hide_timer=self.btns_timer)

        pside = Qt.AlignmentFlag.AlignBottom

        # add top widgets
        self.top_layout.addWidget(self.volume_label)
        self.top_layout.addWidget(self.minmaxbtn)

        self.main_layout.addLayout(self.top_layout, stretch=1)
        self.main_layout.addWidget(self.progressbar, alignment=pside)
        self.main_layout.addLayout(self.ctrls_layout)

    def hide_ctrls(self):
        """ hide control btns on inactivity """
        # stop timer while ctrls are hidden
        self.btns_timer.stop()

        self.snap_btn.hide()
        self.sound_ctrls.hide()
        self.media_ctrls.hide()
        self.order_ctrls.hide()
        # self.tracks_ctrls.hide()

        self.minmaxbtn.hide()
        self.volume_label.hide()
        self.progressbar.hide()
        self.setCursor(Qt.CursorShape.BlankCursor)  # hide cursor

    def show_ctrls(self):
        """ show control btns """

        if not self.height_reduced:
            self.snap_btn.show()
            self.sound_ctrls.show()
            self.media_ctrls.show()
            self.order_ctrls.show()
            # self.tracks_ctrls.show()

            self.volume_label.show()
            self.progressbar.show()

        self.setCursor(Qt.CursorShape.ArrowCursor)  # show cursor
        # start timer to hide
        self.btns_timer.start()
        # always show the resize btn
        self.minmaxbtn.show()

    def update_vol_str(self, value: int):
        """ update volume label to value """
        self.volume_label.setText(f"Volume: {value}%")

    def reduce_height(self, to_value=70):
        """ reduce the frame height to a smaller value """
        if self.height_reduced:
            self.showMaximized()
        else:
            if self.isFullScreen():
                self.showMaximized()
            # get the current width
            current_width = self.width()
            self.resize(current_width, to_value)
            self.hide_ctrls()
        self.height_reduced = not self.height_reduced

    def mouseDoubleClickEvent(self, event):
        """ override double-click events """
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

        return super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """ override mouse move events """
        self.show_ctrls()

        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """ override mouse press events """

        self.btns_timer.stop()

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self.show_ctrls()

        return super().mouseReleaseEvent(event)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])

    win = VidWindow()
    win.showMaximized()

    app.exec()
