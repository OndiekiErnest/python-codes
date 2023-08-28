from vlc import Instance, PlaybackMode, EventType


class VLC():
    """
        python-vlc player
    """

    def __init__(self):
        self._instance = Instance()
        self.playlist = self._instance.media_list_player_new()
        self.media_list = self._instance.media_list_new()
        self._player = self.playlist.get_media_player()
        self._events = self._instance.vlm_get_event_manager()
        self._events.event_attach(
            EventType.MediaParsedChanged, self._wait_data)
        self._repeat = False
        self.media = None
        self.state = "initialized"

    def _release(self):
        # release previous; start a fresh
        self.playlist.stop()
        self.playlist.release()
        self.media_list.release()
        self.playlist, self.media_list = None, None

    def load(self, filename: str) -> str:
        """
            filename: path of media to be played
        """
        self._release()
        self.playlist = self._instance.media_list_player_new()
        self.media_list = self._instance.media_list_new()
        self._player = self.playlist.get_media_player()
        self.loop = self._repeat
        # initialise before getting parsing
        self.data_ready = 0
        self.media = self._instance.media_new(filename)
        self.media.get_mrl()
        self.media.parse_with_options(1, 0)
        self.media_list.add_media(self.media)
        self.playlist.set_media_list(self.media_list)
        self.state = "loaded"
        return self.state

    def _wait_data(self, event):
        # callback for mediaparsed event
        self.data_ready = 1
        print("DATA READY")

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
        return self._player.get_time() / 1000

    def seek(self, pos: float):
        """
            pos: time in ms
        """
        try:
            self._player.set_time(pos)
        except Exception as e:
            print("[Error seeking] :", e)

    def play(self):
        """
            start/resume playing; change mixer state
        """
        self.playlist.play()
        self.state = "playing"

    def pause(self):
        """
            pause playback; change state
        """
        self.playlist.pause()
        self.state = "paused"

    # def previous(self):
    #     self.playlist.previous()

    # def next(self):
    #     self.playlist.next()

    def stop(self):
        """
            stop playing media
        """
        self.playlist.stop()
        self.state = "stopped"

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
        self._repeat = value
        if self._repeat:
            self.playlist.set_playback_mode(PlaybackMode.loop)
        else:
            self.playlist.set_playback_mode(PlaybackMode.default)

    def delete(self):
        """
            reduce refcount of instances
        """
        self.playlist.stop()
        self.playlist.release()
        self.media_list.release()
        self._instance.release()
        self.state = None


if __name__ == "__main__":
    print("[python vlc player]")
