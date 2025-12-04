from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QSlider, QCheckBox, QPushButton,
    QLineEdit, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import secrets
import string
import sys


SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\"'\\|"

# ------------------ MULTILANGUAGE ------------------
LANG = "RU"  # default

STR = {
    "RU": {
        "title": "Генератор паролей | PySide6",
        "theme": "Тема:",
        "light": "Светлая",
        "dark": "Тёмная",
        "length": "Длина пароля: {v}",
        "lower": "Строчные (a-z)",
        "upper": "Заглавные (A-Z)",
        "digits": "Цифры (0-9)",
        "symbols": "Спецсимволы (!@#…)",
        "gen_one": "Сгенерировать один пароль",
        "gen_many": "Сгенерировать 10 паролей",
        "copy": "Копировать пароль",
        "strength": "Сложность: {s}",
        "update": "Скачать обновление",
        "lang": "Язык:" 
    },
    "EN": {
        "title": "Password Generator | PySide6",
        "theme": "Theme:",
        "light": "Light",
        "dark": "Dark",
        "length": "Password length: {v}",
        "lower": "Lowercase (a-z)",
        "upper": "Uppercase (A-Z)",
        "digits": "Digits (0-9)",
        "symbols": "Symbols (!@#…) ",
        "gen_one": "Generate one password",
        "gen_many": "Generate 10 passwords",
        "copy": "Copy password",
        "strength": "Strength: {s}",
        "update": "Download update",
        "lang": "Language:" 
    },
}

# ----------------------------------------------------

def generate_password(length: int, lo: bool, up: bool, dg: bool, sy: bool) -> str:
    alphabet = ""
    if lo: alphabet += string.ascii_lowercase
    if up: alphabet += string.ascii_uppercase
    if dg: alphabet += string.digits
    if sy: alphabet += SYMBOLS
    if not alphabet: return "Error: empty charset"

    required = []
    if lo: required.append(secrets.choice(string.ascii_lowercase))
    if up: required.append(secrets.choice(string.ascii_uppercase))
    if dg: required.append(secrets.choice(string.digits))
    if sy: required.append(secrets.choice(SYMBOLS))
    if len(required) > length: return "Length too small"

    remaining = length - len(required)
    chars = required + [secrets.choice(alphabet) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def rate_strength(pwd: str) -> str:
    score = 0
    if any(c.islower() for c in pwd): score += 1
    if any(c.isupper() for c in pwd): score += 1
    if any(c.isdigit() for c in pwd): score += 1
    if any(c in SYMBOLS for c in pwd): score += 1
    if len(pwd) >= 14: score += 1

    return ["Very Weak", "Weak", "Medium", "Good", "Strong", "Very Strong"][score]


class PasswordGeneratorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_lang = "RU"
        self.setWindowTitle(STR[self.current_lang]["title"])
        self.setFixedSize(480, 540)

        layout = QVBoxLayout()

        # ----- Language Selection -----
        lang_layout = QHBoxLayout()
        lang_label = QLabel(STR[self.current_lang]["lang"])
        self.lang_box = QComboBox()
        self.lang_box.addItems(["Русский", "English"])
        self.lang_box.currentIndexChanged.connect(self.switch_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_box)
        layout.addLayout(lang_layout)

        # ----- Theme -----
        theme_layout = QHBoxLayout()
        self.theme_label = QLabel(STR[self.current_lang]["theme"])
        self.theme_box = QComboBox()
        self.theme_box.addItems([STR[self.current_lang]["light"], STR[self.current_lang]["dark"]])
        self.theme_box.currentIndexChanged.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_box)
        layout.addLayout(theme_layout)

        # ----- Length Slider -----
        self.length_label = QLabel(STR[self.current_lang]["length"].format(v=16))
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(32)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        layout.addWidget(self.length_label)
        layout.addWidget(self.length_slider)

        # ----- Options -----
        self.cb_lower = QCheckBox()
        self.cb_upper = QCheckBox()
        self.cb_digits = QCheckBox()
        self.cb_symbols = QCheckBox()
        for cb in (self.cb_lower, self.cb_upper, self.cb_digits, self.cb_symbols): cb.setChecked(True)
        layout.addWidget(self.cb_lower)
        layout.addWidget(self.cb_upper)
        layout.addWidget(self.cb_digits)
        layout.addWidget(self.cb_symbols)

        # ----- Buttons -----
        btns = QHBoxLayout()
        self.generate_btn = QPushButton()
        self.generate_many_btn = QPushButton()
        self.generate_btn.clicked.connect(self.generate_one)
        self.generate_many_btn.clicked.connect(self.generate_many)
        btns.addWidget(self.generate_btn)
        btns.addWidget(self.generate_many_btn)
        layout.addLayout(btns)

        # ----- Output -----
        self.output = QLineEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.copy_btn = QPushButton(); self.copy_btn.clicked.connect(self.copy_pwd)
        layout.addWidget(self.copy_btn)

        self.strength_label = QLabel()
        layout.addWidget(self.strength_label)

        # Many passwords output
        self.multi_output = QTextEdit(); self.multi_output.setReadOnly(True)
        layout.addWidget(self.multi_output)

        # ----- UPDATE BUTTON -----
        self.update_btn = QPushButton()
        self.update_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Xans434/PasswordGenerator-GPT/releases")))
        layout.addWidget(self.update_btn)

        self.setLayout(layout)
        self.retranslate()
        self.apply_theme()

    # ------------------------ UI UPDATE FUNCTIONS ------------------------
    def update_length_label(self, v):
        self.length_label.setText(STR[self.current_lang]["length"].format(v=v))

    def switch_language(self):
        self.current_lang = "RU" if self.lang_box.currentIndex() == 0 else "EN"
        self.retranslate()

    def retranslate(self):
        txt = STR[self.current_lang]
        self.setWindowTitle(txt["title"])
        self.theme_label.setText(txt["theme"])
        self.theme_box.setItemText(0, txt["light"])
        self.theme_box.setItemText(1, txt["dark"])
        self.length_label.setText(txt["length"].format(v=self.length_slider.value()))

        self.cb_lower.setText(txt["lower"])
        self.cb_upper.setText(txt["upper"])
        self.cb_digits.setText(txt["digits"])
        self.cb_symbols.setText(txt["symbols"])

        self.generate_btn.setText(txt["gen_one"])
        self.generate_many_btn.setText(txt["gen_many"])
        self.copy_btn.setText(txt["copy"])
        self.update_btn.setText(txt["update"])
        self.strength_label.setText(txt["strength"].format(s="–"))

    # ------------------------ GENERATION ------------------------
    def get_flags(self):
        return (
            self.length_slider.value(),
            self.cb_lower.isChecked(),
            self.cb_upper.isChecked(),
            self.cb_digits.isChecked(),
            self.cb_symbols.isChecked(),
        )

    def generate_one(self):
        length, lo, up, dg, sy = self.get_flags()
        pwd = generate_password(length, lo, up, dg, sy)
        self.output.setText(pwd)
        self.strength_label.setText(STR[self.current_lang]["strength"].format(s=rate_strength(pwd)))

    def generate_many(self):
        self.multi_output.clear()
        length, lo, up, dg, sy = self.get_flags()
        for _ in range(10):
            self.multi_output.append(generate_password(length, lo, up, dg, sy))

    def copy_pwd(self):
        QApplication.clipboard().setText(self.output.text())

    # ------------------------ THEMES ------------------------
    def apply_theme(self):
        dark = self.theme_box.currentIndex() == 1
        if dark:
            self.setStyleSheet("""
                QWidget { background:#1e1e1e; color:white; }
                QLineEdit, QTextEdit { background:#2d2d2d; color:white; }
                QPushButton { background:#3a3a3a; color:white; }
            """)
        else:
            self.setStyleSheet("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGeneratorUI()
    window.show()
    sys.exit(app.exec())