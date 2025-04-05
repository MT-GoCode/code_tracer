from PyQt5.QtGui import QColor, QFont

class Theme:
    def __init__(self):
        self.styles = {}
        self.window_bg = QColor()
        self.window_fg = QColor()
        self.menu_bg = QColor()
        self.menu_fg = QColor()

    def apply(self, lexer):
        lexer.setDefaultColor(self.styles["code_default"]["color"])
        lexer.setDefaultPaper(self.styles["code_default"]["paper"])
        lexer.setDefaultFont(QFont("Courier New", 10))

        for style_name, style_data in self.styles.items():
            style_id = getattr(lexer, f"{style_name.upper()}_STYLE")
            lexer.setColor(style_data["color"], style_id)
            lexer.setPaper(style_data["paper"], style_id)
            if "font" in style_data:
                lexer.setFont(style_data["font"], style_id)

    def apply_to_window(self, window):
        palette = window.palette()
        palette.setColor(palette.Window, self.window_bg)
        palette.setColor(palette.WindowText, self.window_fg)
        palette.setColor(palette.Base, self.window_bg)
        palette.setColor(palette.Text, self.window_fg)
        palette.setColor(palette.Button, self.window_bg)
        palette.setColor(palette.ButtonText, self.window_fg)
        window.setPalette(palette)

        menubar = window.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {self.menu_bg.name()};
                color: {self.menu_fg.name()};
            }}
            QMenuBar::item {{
                background-color: {self.menu_bg.name()};
                color: {self.menu_fg.name()};
            }}
            QMenuBar::item:selected {{
                background-color: {self.menu_bg.lighter(120).name()};
            }}
            QMenu {{
                background-color: {self.menu_bg.name()};
                color: {self.menu_fg.name()};
            }}
            QMenu::item:selected {{
                background-color: {self.menu_bg.lighter(120).name()};
            }}
        """)

class LightTheme(Theme):
    def __init__(self):
        super().__init__()
        self.window_bg = QColor("#FFFFFF")
        self.window_fg = QColor("#000000")
        self.menu_bg = QColor("#F0F0F0")
        self.menu_fg = QColor("#000000")
        self.styles = {
            "code_default": {
                "color": QColor("#000000"),
                "paper": QColor("#FFFFFF")
            },
            "code_keyword": {
                "color": QColor("#000080"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_string": {
                "color": QColor("#008000"),
                "paper": QColor("#FFFFFF")
            },
            "code_number": {
                "color": QColor("#800080"),
                "paper": QColor("#FFFFFF")
            },
            "code_comment": {
                "color": QColor("#808080"),
                "paper": QColor("#FFFFFF")
            },
            "text_note": {
                "color": QColor("#000000"),
                "paper": QColor("#eef6ff")
            },
            "file_annotation": {
                "color": QColor("#FFFFFF"),
                "paper": QColor("#444444")
            },
            "code_control": {
                "color": QColor("#8b0000"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_defclass": {
                "color": QColor("#960096"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_builtin": {
                "color": QColor("#00008b"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_bool": {
                "color": QColor("#008b8b"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_import": {
                "color": QColor("#006400"),
                "paper": QColor("#FFFFFF"),
                "font": QFont("Courier New", 10, QFont.Bold)
            }
        }

class DarkTheme(Theme):
    def __init__(self):
        super().__init__()
        self.window_bg = QColor("#1E1E1E")
        self.window_fg = QColor("#FFFFFF")
        self.menu_bg = QColor("#2D2D2D")
        self.menu_fg = QColor("#FFFFFF")
        self.styles = {
            "code_default": {
                "color": QColor("#FFFFFF"),
                "paper": QColor("#000000")
            },
            "code_keyword": {
                "color": QColor("#569CD6"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_string": {
                "color": QColor("#CE9178"),
                "paper": QColor("#000000")
            },
            "code_number": {
                "color": QColor("#B5CEA8"),
                "paper": QColor("#000000")
            },
            "code_comment": {
                "color": QColor("#6A9955"),
                "paper": QColor("#000000")
            },
            "text_note": {
                "color": QColor("#FFFFFF"),
                "paper": QColor("#4682B480")  # Steel blue with 50% transparency
            },
            "file_annotation": {
                "color": QColor("#000000"),
                "paper": QColor("#E0E0E0")  # Near white
            },
            "code_control": {
                "color": QColor("#C586C0"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_defclass": {
                "color": QColor("#DCDCAA"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_builtin": {
                "color": QColor("#4EC9B0"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_bool": {
                "color": QColor("#9CDCFE"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            },
            "code_import": {
                "color": QColor("#4EC9B0"),
                "paper": QColor("#000000"),
                "font": QFont("Courier New", 10, QFont.Bold)
            }
        }