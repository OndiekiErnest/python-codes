__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import pyqtSignal, QObject


class Event(QObject, FileSystemEventHandler):
    """
    file system events handler
    inherits:
        QObject, FileSystemEventHandler
    """

    error = pyqtSignal(str)
    created = pyqtSignal(str)
    deleted = pyqtSignal(str)
    moved = pyqtSignal(str, str)

    def on_created(self, event):
        try:
            if not event.is_directory:
                self.created.emit(event.src_path)
        except Exception as e:
            self.error.emit(e)

    def on_deleted(self, event):
        try:
            if not event.is_directory:
                self.deleted.emit(event.src_path)
        except Exception as e:
            self.error.emit(e)

    def on_moved(self, event):
        """
        on rename
        emits:
            old filename, new filename
            error
        """
        try:
            if not event.is_directory:
                self.moved.emit(event.src_path, event.dest_path)
        except Exception as e:
            self.error.emit(e)


class Watcher():
    """
    file system dir watcher
    """

    def __init__(self, dir_path: str):
        self.watch_dir = dir_path
        self._observer = Observer()
        self.events = Event()

    def observer_start(self):
        """ start watching .watch_dir """
        try:
            self._observer.schedule(self.events, self.watch_dir, recursive=True)
            self._observer.start()
        except FileNotFoundError:
            print("Watcher:stopped:EJECTED")

    def observer_stop(self):
        self._observer.stop()
        self._observer.join()


if __name__ == '__main__':
    watcher = Watcher("C:\\Users\\code\\Music\\Playlists")
    watcher.observer_start()
