from PyQt5.Qsci import QsciLexerCustom
from themes import LightTheme, DarkTheme
from enum import Enum

class LineType(Enum):
    CODE = 0
    TEXT = 1
    FILE_ANNOTATION = 2

class RowData:
    def __init__(self, tabs=0, line_type=LineType.CODE):
        self.tabs = tabs
        self.line_type = line_type

class BaseLexer(QsciLexerCustom):
    CODE_DEFAULT_STYLE   = 0
    CODE_KEYWORD_STYLE   = 1
    CODE_STRING_STYLE    = 2
    CODE_NUMBER_STYLE    = 3
    CODE_COMMENT_STYLE   = 4
    TEXT_NOTE_STYLE      = 5
    FILE_ANNOTATION_STYLE= 6
    CODE_CONTROL_STYLE   = 7
    CODE_DEFCLASS_STYLE  = 8
    CODE_BUILTIN_STYLE   = 9
    CODE_BOOL_STYLE      = 10
    CODE_IMPORT_STYLE    = 11

    def __init__(self, parent=None):
        super().__init__(parent)
        self.themes = {
            "Light": LightTheme(),
            "Dark": DarkTheme()
        }
        self.current_theme = "Dark"  # Default to Dark
        self.themes[self.current_theme].apply(self)

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.themes[theme_name].apply(self)

    def language(self):
        return "BaseLanguage"

    def description(self, style):
        if style == self.CODE_DEFAULT_STYLE:    return "Code: Default"
        if style == self.CODE_KEYWORD_STYLE:    return "Code: Keyword"
        if style == self.CODE_STRING_STYLE:     return "Code: String"
        if style == self.CODE_NUMBER_STYLE:     return "Code: Number"
        if style == self.CODE_COMMENT_STYLE:    return "Code: Comment"
        if style == self.TEXT_NOTE_STYLE:       return "Text Note"
        if style == self.FILE_ANNOTATION_STYLE: return "File Annotation"
        if style == self.CODE_CONTROL_STYLE:    return "Code: Control"
        if style == self.CODE_DEFCLASS_STYLE:   return "Code: Def/Class"
        if style == self.CODE_BUILTIN_STYLE:    return "Code: Built-in"
        if style == self.CODE_BOOL_STYLE:       return "Code: Boolean"
        if style == self.CODE_IMPORT_STYLE:     return "Code: Import"
        return ""

    def styleText(self, start, end):
        editor = self.parent()
        if not editor:
            return
        num_lines = editor.lines()

        for line in range(num_lines):
            line_type = editor.row_data[line].line_type
            text_line = editor.text(line)

            if line_type == LineType.FILE_ANNOTATION:
                self.style_file_line(line, text_line)
            elif line_type == LineType.TEXT:
                self.style_text_line(line, text_line)
            else:
                self.style_code_line(line, text_line)

    def style_file_line(self, line, text):
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)
        length = editor.lineLength(line)
        self.startStyling(pos)
        self.setStyling(length, self.FILE_ANNOTATION_STYLE)

    def style_text_line(self, line, text):
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)
        length = editor.lineLength(line)
        self.startStyling(pos)
        self.setStyling(length, self.TEXT_NOTE_STYLE)

    def style_code_line(self, line, text):
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)
        length = editor.lineLength(line)
        self.startStyling(pos)
        self.setStyling(length, self.CODE_DEFAULT_STYLE)