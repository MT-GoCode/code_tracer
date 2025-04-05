# java_lexer.py

import re
from core_lexer import BaseLexer

class JavaLexer(BaseLexer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.java_keywords = {
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for",
            "goto", "if", "implements", "import", "instanceof", "int",
            "interface", "long", "native", "new", "package", "private",
            "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws",
            "transient", "try", "void", "volatile", "while", "true", "false", "null"
        }

    def language(self):
        return "Java"

    def style_code_line(self, line, text):
        editor = self.parent()
        pos = editor.positionFromLineIndex(line, 0)

        token_regex = re.compile(
            r"""
            (//.*)                    |  # Single-line comment
            (/\*[\s\S]*?\*/)         |  # Multi-line comment
            ("[^"\\]*(\\.[^"\\]*)*") |  # String literal
            ('[^'\\]*(\\.[^'\\]*)*') |  # Char literal
            ([a-zA-Z_][a-zA-Z0-9_]*) |  # Identifiers
            (\d+(\.\d+)?)            |  # Numbers
            (\S)                     # Other
            """,
            re.VERBOSE
        )

        current_idx = 0
        self.startStyling(pos)

        for match in token_regex.finditer(text):
            start_idx = match.start()
            end_idx = match.end()
            if start_idx > current_idx:
                gap_len = start_idx - current_idx
                self.startStyling(pos + current_idx)
                self.setStyling(gap_len, self.CODE_DEFAULT_STYLE)

            token = match.group(0)
            style = self.CODE_DEFAULT_STYLE

            if token.startswith("//") or token.startswith("/*"):
                style = self.CODE_COMMENT_STYLE
            elif token.startswith('"') or token.startswith("'"):
                style = self.CODE_STRING_STYLE
            elif re.match(r'^\d+(\.\d+)?$', token):
                style = self.CODE_NUMBER_STYLE
            elif re.match(r'^[a-zA-Z_]', token):
                if token in self.java_keywords:
                    style = self.CODE_KEYWORD_STYLE

            token_len = end_idx - start_idx
            self.startStyling(pos + start_idx)
            self.setStyling(token_len, style)
            current_idx = end_idx

        # Style trailing gap
        if current_idx < len(text):
            self.startStyling(pos + current_idx)
            self.setStyling(len(text) - current_idx, self.CODE_DEFAULT_STYLE)
