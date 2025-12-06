# -------------------------------------------------------------------
# Приложение разработано ChatGPT для теста подписки Plus
# -------------------------------------------------------------------

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QSlider, QCheckBox, QPushButton,
    QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import secrets
import string
import sys

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\"'\\|"

# ------------------ ТОЛЬКО РУССКИЙ ЯЗЫК ------------------
STR = {
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
    "developed": "Приложение разработано ChatGPT для теста подписки Plus"
}
# ----------------------------------------------------------

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

    return ["Очень слабый", "Слабый", "Средний", "Хороший", "Сильный", "Очень сильный"][score]


class PasswordGeneratorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(STR["title"])
        self.setFixedSize(480, 570)

        layout = QVBoxLayout()

        # ----- Theme -----
        theme_layout = QHBoxLayout()
        self.theme_label = QLabel(STR["theme"])
        self.theme_box = QPushButton(STR["dark"])
        self.theme_box.setCheckable(True)
        self.theme_box.clicked.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_box)
        layout.addLayout(theme_layout)

        # ----- Length Slider -----
        self.length_label = QLabel(STR["length"].format(v=16))
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(8)
        self.length_slider.setMaximum(32)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self.update_length_label)
        layout.addWidget(self.length_label)
        layout.addWidget(self.length_slider)

        # ----- Options -----
        self.cb_lower = QCheckBox(STR["lower"])
        self.cb_upper = QCheckBox(STR["upper"])
        self.cb_digits = QCheckBox(STR["digits"])
        self.cb_symbols = QCheckBox(STR["symbols"])
        for cb in (self.cb_lower, self.cb_upper, self.cb_digits, self.cb_symbols): cb.setChecked(True)
        layout.addWidget(self.cb_lower)
        layout.addWidget(self.cb_upper)
        layout.addWidget(self.cb_digits)
        layout.addWidget(self.cb_symbols)

        # ----- Buttons -----
        btns = QHBoxLayout()
        self.generate_btn = QPushButton(STR["gen_one"])
        self.generate_many_btn = QPushButton(STR["gen_many"])
        self.generate_btn.clicked.connect(self.generate_one)
        self.generate_many_btn.clicked.connect(self.generate_many)
        btns.addWidget(self.generate_btn)
        btns.addWidget(self.generate_many_btn)
        layout.addLayout(btns)

        # ----- Output -----
        self.output = QLineEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.copy_btn = QPushButton(STR["copy"])
        self.copy_btn.clicked.connect(self.copy_pwd)
        layout.addWidget(self.copy_btn)

        self.strength_label = QLabel(STR["strength"].format(s="–"))
        layout.addWidget(self.strength_label)

        self.multi_output = QTextEdit(); self.multi_output.setReadOnly(True)
        layout.addWidget(self.multi_output)

        # ----- UPDATE BUTTON -----
        self.update_btn = QPushButton(STR["update"])
        self.update_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/Xans434/PasswordGenerator-GPT/releases")))
        layout.addWidget(self.update_btn)

        # ----- DEVELOPED LABEL -----
        dev = QLabel(STR["developed"])
        dev.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev)

        self.setLayout(layout)
        self.apply_theme()

    # ------------------------ UI UPDATE FUNCTIONS ------------------------
    def update_length_label(self, v):
        self.length_label.setText(STR["length"].format(v=v))

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
        self.strength_label.setText(STR["strength"].format(s=rate_strength(pwd)))

    def generate_many(self):
        self.multi_output.clear()
        length, lo, up, dg, sy = self.get_flags()
        for _ in range(10):
            self.multi_output.append(generate_password(length, lo, up, dg, sy))

    def copy_pwd(self):
        QApplication.clipboard().setText(self.output.text())

    # ------------------------ THEMES ------------------------
    def apply_theme(self):
        dark = self.theme_box.isChecked()
        self.theme_box.setText(STR["light"] if dark else STR["dark"])

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
