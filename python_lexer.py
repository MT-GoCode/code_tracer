# python_lexer.py

import re
import keyword
import builtins
from core_lexer import BaseLexer

class PythonLexer(BaseLexer):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Build sets of Python keywords/builtins for styling:
        self.py_boolean = {"True", "False", "None"}
        self.py_import = {"import", "from"}
        self.py_defclass = {"def", "class", "lambda"}
        self.py_control = {
            "if", "elif", "else", "while", "for", "break",
            "continue", "return", "try", "raise", "except",
            "finally", "with", "as", "pass"
        }

        all_keywords = set(keyword.kwlist)
        for group in (self.py_boolean, self.py_import, self.py_defclass, self.py_control):
            all_keywords -= group

        self.py_other_keywords = all_keywords
        self.py_builtin = {b for b in dir(builtins) if not b.startswith("_")}

    def language(self):
        return "Python"

    def style_code_line(self, line, text):
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)

        token_regex = re.compile(
            r"""
            ([#].*)                              |  # Comment
            ("[^"\\]*(\\.[^"\\]*)*")            |  # Double-quoted string
            ('[^'\\]*(\\.[^'\\]*)*')            |  # Single-quoted string
            ([a-zA-Z_][a-zA-Z0-9_]*)            |  # Identifiers
            (\d+(\.\d+)?)                       |  # Numbers
            (\S)                                # Other
            """,
            re.VERBOSE
        )

        current_idx = 0
        self.startStyling(pos)

        for match in token_regex.finditer(text):
            start_idx = match.start()
            end_idx = match.end()

            # Style any gap as default
            if start_idx > current_idx:
                gap_len = start_idx - current_idx
                self.startStyling(pos + current_idx)
                self.setStyling(gap_len, self.CODE_DEFAULT_STYLE)

            token = match.group(0)
            style = self.CODE_DEFAULT_STYLE

            if token.startswith("#"):
                style = self.CODE_COMMENT_STYLE
            elif token.startswith('"') or token.startswith("'"):
                style = self.CODE_STRING_STYLE
            elif re.match(r'^\d+(\.\d+)?$', token):
                style = self.CODE_NUMBER_STYLE
            elif re.match(r'^[a-zA-Z_]', token):
                if token in self.py_control:
                    style = self.CODE_CONTROL_STYLE
                elif token in self.py_defclass:
                    style = self.CODE_DEFCLASS_STYLE
                elif token in self.py_builtin:
                    style = self.CODE_BUILTIN_STYLE
                elif token in self.py_boolean:
                    style = self.CODE_BOOL_STYLE
                elif token in self.py_import:
                    style = self.CODE_IMPORT_STYLE
                elif token in self.py_other_keywords:
                    style = self.CODE_KEYWORD_STYLE

            token_len = end_idx - start_idx
            self.startStyling(pos + start_idx)
            self.setStyling(token_len, style)
            current_idx = end_idx

        # Style trailing gap as default
        if current_idx < len(text):
            self.startStyling(pos + current_idx)
            self.setStyling(len(text) - current_idx, self.CODE_DEFAULT_STYLE)
