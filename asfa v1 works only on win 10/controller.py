# the brain for controlling asfa GUI and its data
# import the two
from data import Data
from mainwindow import MainWindow, qt as Qt, ListWidgetItem as QListWidgetItem, threadpool as QThreadPool
import utils
import usb
from qss import QSS
import sys
import os
import psutil


class Controller():

    def __init__(self):
        self.folder_changed = False
        self.gui = MainWindow()
        self.gui.show()
        self.threadpool = QThreadPool()

        self.usb_thread = usb.DeviceListener()
        self.on_startup(self.usb_thread.disks)
        self.usb_thread.signals.on_change.connect(self.update_dropdown_menu)
        self.usb_thread.signals.error.connect(self.gui.banner)
        self.threadpool.start(self.usb_thread)

    def start_up(self):
        """
            populate gui with data
        """

        self.main_tab = self.gui.main_tab
        self.folders_tab = self.gui.disk_man.folders_tab
        self.gui.disk_man.open_button.clicked.connect(self.open_file)
        self.gui.disk_man.select_all_button.clicked.connect(self.select_all)
        self.gui.disk_man.delete_button.clicked.connect(self.remove_file)
        self.folders_tab.currentChanged.connect(self.tab_changed)
        self.gui.disk_man.search_button.clicked.connect(self.on_search)
        self.gui.disk_man.dropdown_menu.currentTextChanged.connect(self.switch)
        for folder in self.data.folders:
            folder_files = self.data.get_files(folder)
            self.gui.disk_man.create_files_list(folder_files)

    def switch(self, path):
        """
            switch between disk paths
            updating path and widgets
        """

        self.data = Data(path)
        self.gui.disk_man.create_disk_win()
        self.gui.disk_man.dropdown_menu.clear()
        self.available_disks.reverse()
        self.gui.disk_man.dropdown_menu.addItems(self.available_disks)
        self.gui.disk_man.dropdown_menu.setCurrentText(path)
        self.start_up()

    def update_dropdown_menu(self, listdrives):
        """
            on insert / on eject
            update available disks list
            simulate switch
        """

        try:
            if listdrives:
                self.available_disks = [d.letter for d in listdrives]
                current = self.gui.disk_man.dropdown_menu.currentText()
                current = current if current in self.available_disks else self.available_disks[
                    0]
                self.switch(current)
            else:
                self.gui.banner("Insert Drive")
        except Exception:  # AttributeError, RuntimeError:
            self.on_startup(listdrives)

    def on_startup(self, listdrives):
        """
            make changes to the dropdown menu
        """

        if listdrives:
            self.available_disks = [d.letter for d in listdrives]
            if self.available_disks:
                self.switch(self.available_disks[0])
        else:
            self.gui.banner("Insert Drive")

    def get_checked_items(self):
        """
            return a list of checked items in list widget
        """

        try:
            items = []
            listwidget = self.folders_tab.currentWidget()
            for index in range(listwidget.count()):
                item = listwidget.item(index)
                if item.checkState() == Qt.Checked:
                    items.append((index, item.text()))
                    item.setCheckState(Qt.Unchecked)
            # change command to select all since get_checked_items unchecks all items
            self.gui.disk_man.select_all_button.setText("Select All")
            self.gui.disk_man.select_all_button.clicked.connect(
                self.select_all)
            return items
        except AttributeError:
            pass

    def delete_list_item(self, index):
        """
            delete an item at index in a list widget
        """

        self.listwidget.takeItem(index)

    def get_folder(self):
        """
            return the currently selected folder path
        """

        try:
            listwidget = self.folders_tab.currentWidget()
            item = listwidget.item(0).text()
            for folder in self.data.folders:
                path = os.path.join(folder, item)
                if os.path.exists(path):
                    break
            return folder
        except AttributeError:
            pass

    def open_file(self):
        """
            open a file using system default app
        """

        self.gui.left_statusbar.setText("Opening file...")
        selected = self.get_checked_items()
        folder = self.get_folder()
        # get the last selected
        try:
            file = selected[-1][1]
            utils.start_file(os.path.join(folder, file))
            self.gui.left_statusbar.setText("File opened!")
        except IndexError:
            self.gui.left_statusbar.setText("Nothing selected")
        except TypeError:
            self.gui.left_statusbar.setText("Widgets not initialized")

    def select_all(self):
        """
            check all list items
        """

        try:
            listwidget = self.folders_tab.currentWidget()
            for index in range(listwidget.count()):
                item = listwidget.item(index)
                item.setCheckState(Qt.Checked)
            self.gui.disk_man.select_all_button.setText("Deselect All")
            self.gui.disk_man.select_all_button.clicked.connect(
                self.deselect_all)
            self.folder_changed = True
        except AttributeError:
            pass

    def deselect_all(self):
        """
            uncheck all list items
        """

        listwidget = self.folders_tab.currentWidget()
        for index in range(listwidget.count()):
            item = listwidget.item(index)
            item.setCheckState(Qt.Unchecked)
        self.gui.disk_man.select_all_button.setText("Select All")
        self.gui.disk_man.select_all_button.clicked.connect(self.select_all)

    def remove_file(self):
        """
            delete selected files permanently
        """

        try:
            selected = self.get_checked_items()
            if selected:
                confirmation = self.gui.ask(
                    f"Delete {len(selected)} selected file(s) permanently?")
                # if confirmation is YES
                if confirmation == 16384:
                    folder = self.get_folder()
                    for index, file in selected[::-1]:
                        path = os.path.join(folder, file)
                        utils.delete_file(path)
                        self.data.files.discard(file)
                        self.delete_list_item(index)
                self.folder_changed = True
        except IndexError:
            pass
        except TypeError:
            pass

    def search_files(self):
        """
            return files matching the search
        """

        results = set()
        search_text = self.gui.disk_man.search_input.text().lower()
        if search_text:
            for file in self.data.files:
                if search_text in file.lower():
                    results.add(file)
            return results

    def on_search(self):
        """
            make changes to the current list widget
        """

        files = self.search_files()
        if files:
            self.addto_listwidget(files)
            self.gui.disk_man.search_button.clicked.connect(self.close_search)
            # self.gui.search_button.setIcon(self.gui.cancel_icon)
            self.gui.disk_man.search_button.setText("Close")
            self.folder_changed = True
        else:
            print("No match!")

    def close_search(self):
        """
            restore files and update search button slot
        """

        self.addto_listwidget(self.data.files)
        self.gui.disk_man.search_button.clicked.connect(self.on_search)
        self.gui.disk_man.search_button.setText("Search")
        self.folder_changed = False

    def tab_changed(self):
        """
            on current tab changed event
        """
        self.restore_folder()
        self.listwidget = self.folders_tab.currentWidget()
        self.data.files = {self.listwidget.item(index).text()
                           for index in range(self.listwidget.count())}
        self.folder_changed = False

    def restore_folder(self):
        """
            uncheck, restore previous listwidget
        """
        if self.folder_changed:
            try:
                self.addto_listwidget(self.data.files)
                self.gui.disk_man.select_all_button.setText("Select All")
                self.gui.disk_man.select_all_button.clicked.connect(
                    self.select_all)
            except AttributeError:
                pass

    def addto_listwidget(self, files):
        """
            update the listwidget with all the files
        """

        self.listwidget.clear()
        for file in files:
            QListWidgetItem(file, self.listwidget).setCheckState(
                Qt.Unchecked)


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # app.setStyleSheet(QSS)
    c = Controller()
    # memory usage in MBs
    memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1048576
    print(f"[MEMORY USED] : {memory_usage} MB")
    sys.exit(app.exec_())
