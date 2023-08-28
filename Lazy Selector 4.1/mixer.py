#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ffpyplayer.player import MediaPlayer
import time
from tinytag import TinyTag
from threading import Thread


class Mixer:
    def __init__(self, source=None):
        ff_opts = {'paused': True, 'autoexit': True,
                   "vn": True, "sn": True, "infbuf": True}
        self.source = source
        try:
            self.player = MediaPlayer(source, ff_opts=ff_opts)
            self.audio = self.player
            Thread(target=self.__run, daemon=True).start()
        except Exception as e:
            print(e)
            self.player = None
            self.audio = None
            pass

    def __run(self):
        self.condition = True
        duration = round(self.duration)
        while self.condition:
            self.l_frame, val = self.player.get_frame()
            if self.l_frame is None:
                time.sleep(0.07)
                if round(self.player.get_pts()) >= duration - 1:
                    self.pause()
                    self.audio = None
                continue
            else:
                self.condition = False

    @property
    def duration(self):
        if self.player is None:
            return
        return TinyTag.get(self.source).duration

    @property
    def time(self):
        if self.player is None:
            return
        return self.player.get_pts()

    @property
    def playing(self):
        if self.player is None:
            return
        return not self.player.get_pause()

    def play(self):
        if self.player is None:
            return

        try:  # pausing audio
            self.player.set_pause(False)
        except Exception:
            pass

    def pause(self):
        if self.player is None:
            return

        try:  # pausing audio
            self.player.set_pause(True)
        except Exception:
            pass

    def seek(self, pts=None, relative=False, accurate=False):
        if pts is None and self.player is None:
            return
        self.player.seek(pts, relative=False, accurate=False)

    # Release the video source when the object is destroyed

    def delete(self):
        if self.player is None:
            return
        self.condition = False
        self.player.set_pause(True)
        self.player.close_player()


if __name__ == '__main__':
    audio = Mixer(
        "C:\\Users\\code\\Videos\\Bomboclaat- DR JOSE CHAMELEONE ft WEASEL.mp4")
    print(round(audio.duration))
    # audio.delete()
    audio.play()
    print(audio.playing)
