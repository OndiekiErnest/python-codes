# utf-8
# the brain for controlling asfa GUI and its data

from mainwindow import MainWindow, qt as Qt, threadpool as QThreadPool
import utils
import usb
from qss import QSS
import sys
import os
import psutil


class Controller():

    def __init__(self):
        self.selected_indexes = []
        self.gui = MainWindow()
        self.gui.show()
        self.gui.select_all_shortcut.activated.connect(self.select_all)

        self.available_disks = ["C:\\Users\\code\\Music",
                                "C:\\Users\\code\\Documents\\May.2019"]
        self.switch(self.available_disks[1])
        # self.threadpool = QThreadPool()
        # self.usb_thread = usb.DeviceListener()
        # self.on_startup(self.usb_thread.disks)
        # self.usb_thread.signals.on_change.connect(self.update_dropdown_menu)
        # self.usb_thread.signals.error.connect(self.gui.banner)
        # self.threadpool.start(self.usb_thread)

    def start_up(self):
        """
            populate gui with data
        """

        for folder in self.folders:
            files = utils.get_files(folder)
            self.gui.disk_man.create_files_list(files, folder)
        self.main_tab = self.gui.main_tab
        self.folders_tab = self.gui.disk_man.folders_tab
        self.folders_tab.currentChanged.connect(self.tab_changed)
        self.gui.disk_man.open_button.clicked.connect(self.open_file)
        self.gui.disk_man.delete_button.clicked.connect(self.remove_file)
        self.gui.disk_man.dropdown_menu.currentTextChanged.connect(self.switch)
        self.gui.on_search_shortcut.activated.connect(self.gui.disk_man.search_input.setFocus)
        # simulate tab_changed
        self.tab_changed()

    def switch(self, path):
        """
            switch between disk paths
            updating path and widgets
        """

        self.folders = utils.get_folders(path)
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
                current = current if current in self.available_disks else self.available_disks[0]
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

    def on_select(self, selected, deselected):
        """
            return a list of checked items in list widget
        """

        selected_row = selected.row()
        deselected_row = deselected.row()
        if deselected_row in self.selected_indexes:
            self.selected_indexes.remove(deselected_row)
        self.selected_indexes.append(selected_row)
        # print(self.selected_indexes)

    def delete_list_item(self, index):
        """
            delete an item at index in a list widget
        """

        self.model.removeRow(index.row())

    def get_path(self, file):
        """
            return the currently selected folder path
            TODO: Improve this function
        """

        try:
            folder = self.folders[self.folders_tab.currentIndex()]
            path = os.path.join(folder, file)
            return path
        except AttributeError:
            pass

    def open_file(self):
        """
            open a file using system default app
        """

        self.gui.left_statusbar.setText("Opening file...")
        selected = self.table_view.selectedIndexes()[0]
        filename = self.get_path(selected.data())
        # get the last selected
        try:
            # index = selected[-1]
            # file = self.model.data(index, Qt.DisplayRole)
            utils.start_file(filename)
            self.gui.left_statusbar.setText("File opened!")
        except IndexError:
            self.gui.left_statusbar.setText("Nothing selected")
        except TypeError:
            self.gui.left_statusbar.setText("Widgets not initialized")

    def remove_file(self):
        """
            delete selected files permanently
        """

        try:
            selected = self.table_view.selectedIndexes()
            if selected:
                confirmation = self.gui.ask(f"Delete {len(selected)} selected file(s) permanently?")
                # if confirmation is YES
                if confirmation == 16384:
                    folder = self.get_path()
                    for index in selected[::-1]:
                        file = self.model.data(index, Qt.DisplayRole)
                        path = os.path.join(folder, file)
                        print(index.data(), path)
                        # utils.delete_file(path)
                        # self.delete_list_item(index)
        except IndexError:
            pass
        except TypeError:
            pass

    def on_search(self):
        """
            slot for search button
        """

        string = self.gui.disk_man.search_input.text()
        self.search(string)

    def search(self, search_txt):
        """
            change the search button icon and set the filter txt
        """

        if search_txt:
            self.model.setFilterRegExp(search_txt)
            self.gui.disk_man.search_button.setIcon(self.gui.cancel_icon)
            self.gui.disk_man.search_button.clicked.connect(self.close_search)
        else:
            self.close_search()

    def close_search(self):
        """
            restore files and update search button slot
        """

        self.gui.disk_man.search_button.setIcon(self.gui.disk_man.search_icon)
        self.gui.disk_man.search_button.clicked.connect(self.on_search)
        self.gui.disk_man.search_input.clear()
        self.model.setFilterRegExp("")

    def tab_changed(self):
        """
            on current tab changed event
        """

        self.table_view = self.folders_tab.currentWidget()
        self.table_view.setFocus()
        self.model = self.table_view.model()
        self.gui.disk_man.search_input.textChanged.connect(self.search)
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.currentRowChanged.connect(self.on_select)
        self.close_search()

    # @pyqtSlot()
    def select_all(self):
        """
            select all table items
        """

        self.table_view.selectAll()


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    c = Controller()
    # memory usage in MBs
    memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1048576
    print(f"[MEMORY USED] : {memory_usage} MB")
    sys.exit(app.exec_())
