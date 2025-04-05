# semantic_editor.py

import re
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtWidgets import QAction, QApplication
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer
from core_lexer import LineType, RowData, BaseLexer

class SemanticEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spaces_per_tab = 4

        # The one shared row_data for the entire document
        self.row_data = []

        font = QFont("Courier New", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setUtf8(True)
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setTabWidth(self.spaces_per_tab)
        self.setIndentationsUseTabs(False)

        self.setFolding(QsciScintilla.BoxedFoldStyle)

        # Start with a generic BaseLexer (will be replaced in MainWindow)
        self.setLexer(BaseLexer(self))

        self.last_line_count = 0

        self.filter_folded_copy_enabled = True
        self.copy_action = QAction("Filter Out Folded Lines on Copy", self)
        self.copy_action.setCheckable(True)
        self.copy_action.setChecked(True)
        self.copy_action.triggered.connect(self.toggle_folded_copy_filter)

        self.customContextMenuRequested.connect(self.show_custom_context_menu)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Connect signals
        self.linesChanged.connect(self.on_lines_changed)
        self.textChanged.connect(lambda: QTimer.singleShot(0, self.on_text_changed))

        # Initialize row_data for however many lines we start with (often 1 empty line).
        self.init_row_data()

    def init_row_data(self):
        line_count = self.lines()
        self.row_data = [RowData(0, LineType.CODE) for _ in range(line_count)]
        self.last_line_count = line_count

    def toggle_folded_copy_filter(self):
        self.filter_folded_copy_enabled = not self.filter_folded_copy_enabled

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy) and self.filter_folded_copy_enabled:
            self.copy_filtered_text()
        else:
            super().keyPressEvent(event)

    def show_custom_context_menu(self, pos):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(self.copy_action)
        menu.exec_(self.mapToGlobal(pos))

    def copy_filtered_text(self):
        if self.hasSelectedText():
            start_line, _, end_line, _ = self.getSelection()
            visible_lines = []
            for line in range(start_line, end_line + 1):
                if self.SendScintilla(QsciScintilla.SCI_GETLINEVISIBLE, line):
                    visible_lines.append(self.text(line))
            if visible_lines:
                QApplication.clipboard().setText("\n".join(visible_lines))

    def on_text_changed(self):
        """
        If line count didn't change, we only update indentation/folding.
        """
        if self.lines() == self.last_line_count:
            self.setReadOnly(True)
            self.update_row_data()
            self.apply_folding()
            self.setReadOnly(False)

    def on_lines_changed(self):
        """
        If the line count changed, rely on update_row_data() to handle it safely.
        """
        self.setReadOnly(True)
        self.last_line_count = self.lines()
        self.update_row_data()
        self.apply_folding()
        self.setReadOnly(False)

    def update_row_data(self):
        """
        Re-align row_data length with the number of lines.
        Then recalc indentation and restyle the editor.
        """
        line_count = self.lines()

        # If the editor shrank, truncate row_data
        if line_count < len(self.row_data):
            self.row_data = self.row_data[:line_count]
        # If the editor grew, add new lines, guessing line type from the last known line
        elif line_count > len(self.row_data):
            needed = line_count - len(self.row_data)
            # If we have at least one line in row_data, replicate the last line's type
            if self.row_data:
                last_type = self.row_data[-1].line_type
            else:
                last_type = LineType.CODE
            for _ in range(needed):
                # If the last line was TEXT, new lines become TEXT; else CODE
                new_line_type = LineType.TEXT if last_type == LineType.TEXT else LineType.CODE
                self.row_data.append(RowData(0, new_line_type))

        # Recalculate indentation
        for i in range(line_count):
            line_text = self.text(i)
            leading_spaces = len(line_text) - len(line_text.lstrip(' '))
            self.row_data[i].tabs = leading_spaces // self.spaces_per_tab

        # Force restyling
        if self.lexer():
            self.lexer().styleText(0, 0)

    def apply_folding(self):
        SC_FOLDLEVELBASE = 0x0000
        SC_FOLDLEVELHEADERFLAG = 0x2000

        line_count = self.lines()
        for i in range(line_count):
            indent = self.row_data[i].tabs
            fold_level = SC_FOLDLEVELBASE + indent

            if i + 1 < line_count:
                next_indent = self.row_data[i+1].tabs
                if next_indent > indent:
                    fold_level |= SC_FOLDLEVELHEADERFLAG

            self.SendScintilla(QsciScintilla.SCI_SETFOLDLEVEL, i, fold_level)

    def set_line_type(self, line_idx, line_type):
        self.beginUndoAction()
        self.row_data[line_idx].line_type = line_type
        if self.lexer():
            self.lexer().styleText(0, 0)
        self.endUndoAction()

    def set_current_line_type(self, line_type):
        self.beginUndoAction()
        if self.hasSelectedText():
            start_line, _, end_line, _ = self.getSelection()
            for line_idx in range(start_line, end_line + 1):
                self.row_data[line_idx].line_type = line_type
        else:
            current_line = self.getCursorPosition()[0]
            self.row_data[current_line].line_type = line_type
        if self.lexer():
            self.lexer().styleText(0, 0)
        self.endUndoAction()

    def set_tab_size(self, size):
        self.spaces_per_tab = size
        self.setTabWidth(size)
        self.update_row_data()
        self.apply_folding()
