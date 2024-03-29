__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"
__version__ = "4.2"

from os.path import dirname, abspath, join
from os import environ
import sys

BASE_DIR = dirname(abspath(__file__))


def r_path(relpath):
    """
        Get absolute path
    """

    base_path = getattr(sys, "_MEIPASS", BASE_DIR)
    return join(base_path, relpath)


VLC_DIR = r_path("mixer")
DLL_DIR = join(VLC_DIR, "libvlc.dll")
""" set environment variables for vlc to use """
environ.setdefault("PYTHON_VLC_MODULE_PATH", VLC_DIR)
environ.setdefault("PYTHON_VLC_LIB_PATH", DLL_DIR)

from vlc import Instance, PlaybackMode, MediaParsedStatus


class VLC():
    """
        python-vlc player
    """

    def __init__(self):
        self._instance = Instance(("--no-video", "--quiet"))
        self.playlist = self._instance.media_list_player_new()
        self.media_list = self._instance.media_list_new()
        self._player = self.playlist.get_media_player()
        self._repeat = False
        self.media = None

    def _release(self):
        # release previous; start a fresh
        self.playlist.stop()
        self.playlist.release()
        self.media_list.release()
        if self.media is not None:
            self.media.release()
        self.media, self.playlist, self.media_list = None, None, None
        self._player = None

    def load(self, filename: str) -> str:
        """
            filename: path of media to be played
        """
        self._release()
        self.playlist = self._instance.media_list_player_new()
        self.media_list = self._instance.media_list_new()
        self._player = self.playlist.get_media_player()
        # set playback mode to bool stored in _repeat
        self.loop = self._repeat
        self.media = self._instance.media_new(filename)
        resource = self.media.get_mrl()
        # parser returns 0 on success
        self.media.parse_with_options(1, 0)
        # self.media.parse()
        self.media_list.add_media(self.media)
        self.playlist.set_media_list(self.media_list)
        return resource

    @property
    def duration(self) -> float:
        """
            return media duration in seconds
        """
        # while not self.data_ready:
        if self.media is not None:
            return self.media.get_duration() / 1000

    @property
    def time(self) -> float:
        """
            return elapsed time in seconds
        """
        if self._player is not None:
            return self._player.get_time() / 1000

    def seek(self, pos: float):
        """
            pos: time in ms
        """
        if self._player is not None:
            try:
                self._player.set_time(pos)
            except Exception as e:
                print("[Error seeking] :", e)

    def play(self):
        """
            start/resume playing; change mixer state
        """
        if self.playlist is not None:
            self.playlist.play()

    def pause(self):
        """
            pause playback; change state
        """
        if self.playlist is not None:
            self.playlist.pause()

    def stop(self):
        """
            stop playing media
        """
        if self.playlist is not None:
            self.playlist.stop()

    @property
    def loop(self) -> bool:
        """
            get the playback mode
        """
        return self._repeat

    @loop.setter
    def loop(self, value: bool):
        """
            set playback mode
        """
        if type(value) is bool and self.playlist is not None:
            self._repeat = value
            if self._repeat:
                self.playlist.set_playback_mode(PlaybackMode.loop)
            else:
                self.playlist.set_playback_mode(PlaybackMode.default)

    @property
    def state(self):
        if self.playlist is not None:
            return self.playlist.get_state()

    @property
    def data_ready(self) -> bool:
        if self.media is not None:
            return self.media.get_parsed_status() == MediaParsedStatus.done

    def delete(self):
        """
            reduce refcount of instances
        """
        self._release()
        self._instance.release()


if __name__ == "__main__":
    print("[python vlc player]")
