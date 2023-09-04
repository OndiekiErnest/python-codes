from PyQt6.QtWidgets import (
    QLineEdit, QCompleter,
    QFileDialog,
)
from PyQt6.QtCore import (
    QStringListModel, Qt,
    QSortFilterProxyModel,
    QRegularExpression,
)
from PyQt6.QtGui import (
    QIcon, QAction,
)
from os.path import (
    abspath, dirname,
    join, exists,
    normpath, expanduser,
)
from os import sep as SEP

BASE_DIR = abspath(dirname(__file__))
DATA_DIR = join(BASE_DIR, "data")

# files
CANCEL = join(DATA_DIR, "cancel.png")
FIND = join(DATA_DIR, "search.png")
ERROR = join(DATA_DIR, "error.png")
ADD_FOLDER = join(DATA_DIR, "add_folder.png")
SHOW = join(DATA_DIR, "show.png")
HIDE = join(DATA_DIR, "hide.png")


class Completer(QCompleter):
    """ custom completer for showing suggestions """

    __slots__ = ("local_prefix", "source_model",
                 "filter_model", "using_original_model")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.local_prefix = ""
        self.source_model = None
        self.filter_model = QSortFilterProxyModel(self)
        self.using_original_model = False

    def setModel(self, model):
        if isinstance(model, (list, tuple, set)):
            model = QStringListModel(model)
        self.source_model = model
        self.filter_model = QSortFilterProxyModel(self)
        self.filter_model.setSourceModel(self.source_model)
        super().setModel(self.filter_model)
        self.using_original_model = True

    def updateModel(self):
        if not self.using_original_model:
            self.filter_model.setSourceModel(self.source_model)

        pattern = QRegularExpression(self.local_prefix,
                                     QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.filter_model.setFilterRegularExpression(pattern)

    def splitPath(self, path):
        self.local_prefix = path
        self.updateModel()
        if self.filter_model.rowCount() == 0:
            self.using_original_model = False
            self.filter_model.setSourceModel(QStringListModel([path]))
            return [path]
        return []


class SearchInput(QLineEdit):
    """
    custom QLineEdit for search
    """
    __slots__ = ("close_action", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.close_action = QAction(self)
        self.close_action.setIcon(QIcon(CANCEL))
        self.close_action.triggered.connect(self.close_search)

        self.addAction(QIcon(FIND), QLineEdit.ActionPosition.LeadingPosition)
        self.textChanged.connect(self.on_type)

    def close_search(self):
        """ clear search area and change icon """
        self.clear()
        self.removeAction(self.close_action)

    def on_type(self, txt):
        """ change icon, close on action triggered """
        if txt:
            self.addAction(self.close_action, QLineEdit.ActionPosition.TrailingPosition)
        else:
            self.removeAction(self.close_action)


class LineEdit(QLineEdit):
    """
    custom QLineEdit that:
    - shows error icon if it is empty on text() call
    - shows suggestions on typing
    """

    __slots__ = ("error_action", "suggestions", "prev_text", "comp")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.error_action = QAction()
        self.error_action.setIcon(QIcon(ERROR))

        self.suggestions = set()
        self.prev_text = ""

        self.comp = Completer(parent=self)
        self.comp.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCompleter(self.comp)

    def add_suggestions(self, suggestions):
        """ add unique suggestion """
        self.suggestions.update(suggestions)
        self.comp.setModel(self.suggestions)

    def focusInEvent(self, e):
        current_text = self.text()
        if current_text:
            self.prev_text = current_text

        super().focusInEvent(e)

    def focusOutEvent(self, e):
        current_text = self.text()
        if not current_text:
            self.setText(self.prev_text)
        super().focusOutEvent(e)

    def keyPressEvent(self, e):
        key = e.key()
        if (key == Qt.Key.Key_Return) or (key == Qt.Key.Key_Enter):
            # avoid setting an empty str
            self.comp.popup().hide()
            text = self.comp.currentCompletion()
            self.setText(text)
            e.accept()
        else:
            return super().keyPressEvent(e)

    def text(self):
        text = super().text()
        if text:
            self.remove_error()
        else:
            self.error_action.setToolTip("This field is required")
            self.raise_error()
        self.update()
        return text

    def setText(self, text: str):
        """ remove error icon if text """
        if text:
            self.remove_error()
        # else:
        #     self.raise_error()
        self.update()
        # set text
        super().setText(text)

    def remove_error(self):
        """ remove error icon """
        try:
            self.error_action.setToolTip("This field is required")
            self.removeAction(self.error_action)
        except Exception:
            pass

    def raise_error(self):
        """ add error icon """
        try:
            self.addAction(self.error_action, QLineEdit.ActionPosition.LeadingPosition)
        except Exception:
            pass


class PathEdit(LineEdit):
    """
    custom QLineEdit for path display, set to readOnly
    """
    __slots__ = ("caption", "last_known_dir", )

    def __init__(self, chooser_title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.caption = chooser_title
        self.last_known_dir = expanduser(f"~{SEP}Documents")

        self.textChanged.connect(self.validate)
        self.setToolTip("Click folder icon to browse")

        add_action = QAction(self)
        add_action.setObjectName("addPathAction")
        add_action.setIcon(QIcon(ADD_FOLDER))
        add_action.setToolTip("Browse")
        add_action.triggered.connect(self.get_dir)
        self.addAction(add_action, QLineEdit.ActionPosition.TrailingPosition)
        # disable input
        self.setReadOnly(True)

    def get_dir(self):
        """ set abs folder str """
        folder = normpath(QFileDialog.getExistingDirectory(
            self, caption=f"{self.caption}",
            directory=self.last_known_dir,
        ))
        if folder and folder != ".":
            self.last_known_dir = folder
            self.setText(folder)

    def text(self):
        """ return a text str if it's a valid path """
        text = super().text()
        # raise errors if any
        self.validate(text)
        if not exists(text):
            text = ""
        return text

    def validate(self, text: str):
        """ set error icon if path does not exist """
        if text:
            if exists(text):
                self.remove_error()
            else:
                self.error_action.setToolTip("The path does not exist")
                self.raise_error()


class MaskedEdit(LineEdit):
    """
    custom QLineEdit for masked display, with show/hide
    """
    __slots__ = ("show_action", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set masked input
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_action = QAction(self)
        self.show_action.setToolTip("Show")
        self.show_action.setIcon(QIcon(SHOW))
        # since it defaults to hide, show on first click
        self.show_action.triggered.connect(self.set_show)
        self.addAction(self.show_action, QLineEdit.ActionPosition.TrailingPosition)

    def set_show(self):
        """ show contents """
        self.show_action.triggered.disconnect()
        self.show_action.setToolTip("Hide")
        self.show_action.setIcon(QIcon(HIDE))
        self.setEchoMode(QLineEdit.EchoMode.Normal)
        # when clicked again, hide
        self.show_action.triggered.connect(self.set_hide)

    def set_hide(self):
        """ hide contents """
        self.show_action.triggered.disconnect()
        self.show_action.setToolTip("Show")
        self.show_action.setIcon(QIcon(SHOW))
        self.setEchoMode(QLineEdit.EchoMode.Password)
        # when clicked again, show
        self.show_action.triggered.connect(self.set_show)
