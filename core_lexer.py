# core_lexer.py

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor, QFont
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
    """
    A base lexer that no longer stores its own row_data.
    Instead, it looks up row_data in its parent editor.
    """
    # Style indices:
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
        self.setup_styles()

    def setup_styles(self):
        self.setDefaultColor(QColor("#000000"))
        self.setDefaultPaper(QColor("#FFFFFF"))
        self.setDefaultFont(QFont("Courier New", 10))

        # Default code style
        self.setColor(QColor("#000000"), self.CODE_DEFAULT_STYLE)
        self.setPaper(QColor("#FFFFFF"), self.CODE_DEFAULT_STYLE)

        # Keyword style
        self.setColor(QColor("#000080"), self.CODE_KEYWORD_STYLE)
        kw_font = QFont("Courier New", 10)
        kw_font.setBold(True)
        self.setFont(kw_font, self.CODE_KEYWORD_STYLE)

        # String style
        self.setColor(QColor("#008000"), self.CODE_STRING_STYLE)

        # Number style
        self.setColor(QColor("#800080"), self.CODE_NUMBER_STYLE)

        # Comment style
        self.setColor(QColor("#808080"), self.CODE_COMMENT_STYLE)

        # Text note style
        self.setColor(QColor("#000000"), self.TEXT_NOTE_STYLE)
        self.setPaper(QColor("#eef6ff"), self.TEXT_NOTE_STYLE)

        # File annotation style
        self.setColor(QColor("#FFFFFF"), self.FILE_ANNOTATION_STYLE)
        self.setPaper(QColor("#444444"), self.FILE_ANNOTATION_STYLE)

        # Control statements
        self.setColor(QColor("#8b0000"), self.CODE_CONTROL_STYLE)
        ctrl_font = QFont("Courier New", 10)
        ctrl_font.setBold(True)
        self.setFont(ctrl_font, self.CODE_CONTROL_STYLE)

        # Def/class style
        self.setColor(QColor("#960096"), self.CODE_DEFCLASS_STYLE)
        dc_font = QFont("Courier New", 10)
        dc_font.setBold(True)
        self.setFont(dc_font, self.CODE_DEFCLASS_STYLE)

        # Builtins
        self.setColor(QColor("#00008b"), self.CODE_BUILTIN_STYLE)
        bi_font = QFont("Courier New", 10)
        bi_font.setBold(True)
        self.setFont(bi_font, self.CODE_BUILTIN_STYLE)

        # Booleans
        self.setColor(QColor("#008b8b"), self.CODE_BOOL_STYLE)
        bool_font = QFont("Courier New", 10)
        bool_font.setBold(True)
        self.setFont(bool_font, self.CODE_BOOL_STYLE)

        # Import style
        self.setColor(QColor("#006400"), self.CODE_IMPORT_STYLE)
        imp_font = QFont("Courier New", 10)
        imp_font.setBold(True)
        self.setFont(imp_font, self.CODE_IMPORT_STYLE)

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
        """
        We'll iterate over every line in the editor, check the editor's row_data,
        and dispatch to style_code_line / style_text_line / style_file_line as appropriate.
        """
        editor = self.parent()
        if not editor:
            return
        num_lines = editor.lines()

        for line in range(num_lines):
            # Grab the line type from the editor's shared row_data
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
        """
        Subclasses will override this with real tokenization logic for Python, C++, Java, etc.
        Default = no token-based styling, just default code style.
        """
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)
        length = editor.lineLength(line)
        self.startStyling(pos)
        self.setStyling(length, self.CODE_DEFAULT_STYLE)
