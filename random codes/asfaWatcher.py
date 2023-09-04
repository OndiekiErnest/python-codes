__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import pyqtSignal, QObject


logging.basicConfig(level=logging.DEBUG)
watcher_logger = logging.getLogger(__name__)
watcher_logger.info(f">>> Initializing {__name__}")


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
            watcher_logger.error(f">>> Error on_created: {e}")

    def on_deleted(self, event):
        try:
            if not event.is_directory:
                self.deleted.emit(event.src_path)
        except Exception as e:
            self.error.emit(e)
            watcher_logger.error(f">>> Error on_deleted: {e}")

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
            watcher_logger.error(f">>> Error on_moved: {e}")


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
        watcher_logger.info(">>> Starting watcher observer thread")
        try:
            self._observer.schedule(self.events, self.watch_dir, recursive=True)
            self._observer.start()
        except Exception as e:  # FileNotFoundError...
            watcher_logger.error(f">>> Watcher:stopped: {e}")

    def observer_stop(self):
        watcher_logger.info(">>> Stopping watcher observer")
        self._observer.stop()
        self._observer.join()
        watcher_logger.info(">>> Stopped successfully")


if __name__ == '__main__':
    import os
    watcher = Watcher(os.path.expanduser(f"{os.sep}Desktop"))
    watcher.observer_start()
