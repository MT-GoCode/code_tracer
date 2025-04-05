import sys
import os
import json

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QMenu, QAction, QShortcut, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QColor

from semantic_editor import SemanticEditor
from core_lexer import LineType
from python_lexer import PythonLexer
from cpp_lexer import CppLexer
from java_lexer import JavaLexer
from themes import LightTheme, DarkTheme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Code Trace Editor")
        self.unsaved_changes = False
        self.current_filename = "untitled.trace"
        self.current_language_name = "Python"
        self.current_theme = "Dark"
        self.themes = {
            "Light": LightTheme(),
            "Dark": DarkTheme()
        }

        # Create editor
        self.editor = SemanticEditor()

        # Create language lexers
        self.python_lexer = PythonLexer(self.editor)
        self.cpp_lexer = CppLexer(self.editor)
        self.java_lexer = JavaLexer(self.editor)

        # Default language: Python
        self.editor.setLexer(self.python_lexer)

        self.language_actions = {}
        self.tabsize_actions = {}
        self.theme_actions = {}

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Menubar
        menubar = self.menuBar()

        # FILE menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open…", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As…", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # EDIT menu
        edit_menu = menubar.addMenu("Edit")
        line_type_menu = QMenu("Line Type", self)
        edit_menu.addMenu(line_type_menu)

        code_action = QAction("Code (Alt+1)", self)
        code_action.triggered.connect(lambda: self.set_line_type(LineType.CODE))
        line_type_menu.addAction(code_action)

        text_action = QAction("Text Note (Alt+2)", self)
        text_action.triggered.connect(lambda: self.set_line_type(LineType.TEXT))
        line_type_menu.addAction(text_action)

        file_action = QAction("File Annotation (Alt+3)", self)
        file_action.triggered.connect(lambda: self.set_line_type(LineType.FILE_ANNOTATION))
        line_type_menu.addAction(file_action)

        # LANGUAGE menu
        language_menu = menubar.addMenu("Language")

        def make_lang_action(name, fn):
            action = QAction(name, self)
            action.setCheckable(True)
            action.triggered.connect(fn)
            language_menu.addAction(action)
            self.language_actions[name] = action
            return action

        make_lang_action("Python", self.use_python_lexer)
        make_lang_action("C++", self.use_cpp_lexer)
        make_lang_action("Java", self.use_java_lexer)

        # OPTIONS menu
        options_menu = menubar.addMenu("Options")
        
        # Tab size submenu
        tabsize_menu = QMenu("Tab Size", self)
        options_menu.addMenu(tabsize_menu)

        for size in [2, 4, 8]:
            act = QAction(str(size), self)
            act.setCheckable(True)
            act.triggered.connect(lambda _, s=size: self.set_tab_size(s))
            tabsize_menu.addAction(act)
            self.tabsize_actions[size] = act

        # Theme submenu
        theme_menu = QMenu("Theme", self)
        options_menu.addMenu(theme_menu)

        def make_theme_action(name, fn):
            action = QAction(name, self)
            action.setCheckable(True)
            action.triggered.connect(fn)
            theme_menu.addAction(action)
            self.theme_actions[name] = action
            return action

        make_theme_action("Dark", self.use_dark_theme)
        make_theme_action("Light", self.use_light_theme)

        options_menu.addAction(self.editor.copy_action)

        # Keyboard shortcuts for line types
        self.setup_keyboard_shortcuts()

        # Connect signals to detect changes => unsaved
        self.editor.textChanged.connect(self.mark_unsaved)

        self.init_default_states()

    def init_default_states(self):
        self.set_tab_size(4)
        self.update_language_checkmarks("Python")
        self.use_dark_theme()  # Default to dark
        self.update_title()

    def setup_keyboard_shortcuts(self):
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_1), self).activated.connect(
            lambda: self.set_line_type(LineType.CODE))
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_2), self).activated.connect(
            lambda: self.set_line_type(LineType.TEXT))
        QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_3), self).activated.connect(
            lambda: self.set_line_type(LineType.FILE_ANNOTATION))

    def mark_unsaved(self):
        self.unsaved_changes = True
        self.update_title()

    def mark_saved(self):
        self.unsaved_changes = False
        self.update_title()

    def update_title(self):
        base_name = os.path.basename(self.current_filename)
        title = f"Code Trace Editor - {base_name}"
        if self.unsaved_changes:
            title += "*"
        self.setWindowTitle(title)

    # Theme methods
    def use_dark_theme(self):
        
        self.current_theme = "Dark"
        self.themes["Dark"].apply(self.python_lexer)
        self.themes["Dark"].apply(self.cpp_lexer)
        self.themes["Dark"].apply(self.java_lexer)
        self.themes["Dark"].apply_to_window(self)
        self.editor.setLexer(self.editor.lexer())  # Force restyle
        self.editor.setMarginsBackgroundColor(self.themes["Dark"].window_bg)
        self.editor.setMarginsForegroundColor(self.themes["Dark"].window_fg)
        self.editor.setCaretForegroundColor(QColor("#FFFFFF"))
        self.update_theme_checkmarks("Dark")
        self.mark_unsaved()

    def use_light_theme(self):
        self.current_theme = "Light"
        self.themes["Light"].apply(self.python_lexer)
        self.themes["Light"].apply(self.cpp_lexer)
        self.themes["Light"].apply(self.java_lexer)
        self.themes["Light"].apply_to_window(self)
        self.editor.setLexer(self.editor.lexer())  # Force restyle
        self.editor.setMarginsBackgroundColor(self.themes["Light"].window_bg)
        self.editor.setMarginsForegroundColor(self.themes["Light"].window_fg)
        self.update_theme_checkmarks("Light")
        self.mark_unsaved()

    def update_theme_checkmarks(self, selected_theme):
        for name, action in self.theme_actions.items():
            action.setChecked(name == selected_theme)

    # Language methods
    def use_python_lexer(self):
        self.editor.setLexer(self.python_lexer)
        self.themes[self.current_theme].apply(self.python_lexer)
        self.editor.update_row_data()
        self.editor.apply_folding()
        self.update_language_checkmarks("Python")
        self.current_language_name = "Python"
        self.mark_unsaved()

    def use_cpp_lexer(self):
        self.editor.setLexer(self.cpp_lexer)
        self.themes[self.current_theme].apply(self.cpp_lexer)
        self.editor.update_row_data()
        self.editor.apply_folding()
        self.update_language_checkmarks("C++")
        self.current_language_name = "C++"
        self.mark_unsaved()

    def use_java_lexer(self):
        self.editor.setLexer(self.java_lexer)
        self.themes[self.current_theme].apply(self.java_lexer)
        self.editor.update_row_data()
        self.editor.apply_folding()
        self.update_language_checkmarks("Java")
        self.current_language_name = "Java"
        self.mark_unsaved()

    def update_language_checkmarks(self, selected_lang):
        for name, action in self.language_actions.items():
            action.setChecked(name == selected_lang)

    def set_line_type(self, line_type):
        self.editor.set_current_line_type(line_type)
        self.mark_unsaved()

    def set_tab_size(self, size):
        self.editor.set_tab_size(size)
        self.update_tabsize_checkmarks(size)
        self.mark_unsaved()

    def update_tabsize_checkmarks(self, selected_size):
        for size, action in self.tabsize_actions.items():
            action.setChecked(size == selected_size)

    def new_file(self):
        if not self.check_save_if_needed():
            return
        self.editor.clear()
        self.editor.row_data.clear()
        self.editor.init_row_data()
        self.current_filename = "untitled.trace"
        self.current_language_name = "Python"
        self.editor.setLexer(self.python_lexer)
        self.themes[self.current_theme].apply(self.python_lexer)
        self.update_language_checkmarks("Python")
        self.set_tab_size(4)
        self.mark_saved()

    def open_file(self):
        if not self.check_save_if_needed():
            return
        dialog = QFileDialog(self, "Open File", ".", "Trace Files (*.trace);;All Files (*)")
        if dialog.exec_() != QFileDialog.Accepted:
            return
        filename = dialog.selectedFiles()[0]
        if not os.path.exists(filename):
            return
        self.load_trace_file(filename)

    def save_file(self):
        if self.current_filename == "untitled.trace" and not os.path.exists(self.current_filename):
            self.save_file_as()
        else:
            self.do_save(self.current_filename)

    def save_file_as(self):
        dialog = QFileDialog(self, "Save File As", ".", "Trace Files (*.trace);;All Files (*)")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.selectFile(os.path.basename(self.current_filename))

        if dialog.exec_() != QFileDialog.Accepted:
            return
        filename = dialog.selectedFiles()[0]
        if not filename.lower().endswith(".trace"):
            filename += ".trace"
        self.do_save(filename)

    def do_save(self, filename):
        data = {}
        data["tab_size"] = self.editor.spaces_per_tab
        data["language"] = self.current_language_name
        data["theme"] = self.current_theme

        row_data_list = []
        for rd in self.editor.row_data:
            row_data_list.append({
                "tabs": rd.tabs,
                "line_type": rd.line_type.value
            })
        data["row_data"] = row_data_list

        data["text"] = self.editor.text()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.current_filename = filename
        self.mark_saved()

    def load_trace_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = data.get("text", "")
        row_data_list = data.get("row_data", [])
        tab_size = data.get("tab_size", 4)
        language = data.get("language", "Python")
        theme = data.get("theme", "Dark")

        self.editor.clear()
        self.editor.row_data.clear()
        self.editor.setText(text)
        self.editor.update()

        self.editor.init_row_data()
        line_count = self.editor.lines()
        for i, rd_dict in enumerate(row_data_list):
            if i < line_count:
                self.editor.row_data[i].tabs = rd_dict.get("tabs", 0)
                self.editor.row_data[i].line_type = LineType(rd_dict.get("line_type", 0))

        self.set_tab_size(tab_size)
        if language == "Python":
            self.use_python_lexer()
        elif language == "C++":
            self.use_cpp_lexer()
        elif language == "Java":
            self.use_java_lexer()
        else:
            self.use_python_lexer()

        if theme == "Dark":
            self.use_dark_theme()
        else:
            self.use_light_theme()

        self.current_filename = filename
        self.mark_saved()

    def check_save_if_needed(self):
        if not self.unsaved_changes:
            return True
        ret = QMessageBox.warning(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Save before proceeding?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        if ret == QMessageBox.Save:
            self.save_file()
            return True
        elif ret == QMessageBox.Discard:
            return True
        else:
            return False

    def closeEvent(self, event):
        if not self.check_save_if_needed():
            event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()