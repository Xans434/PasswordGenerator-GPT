from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QSlider, QCheckBox, QPushButton,
    QLineEdit, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
import secrets
import string
import sys


SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/\"'\\|"


def generate_password(length: int,
                      use_lower: bool,
                      use_upper: bool,
                      use_digits: bool,
                      use_symbols: bool) -> str:

    alphabet = ""
    if use_lower:
        alphabet += string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        alphabet += SYMBOLS

    if not alphabet:
        return "Ошибка: пустой набор символов"

    required = []
    if use_lower:
        required.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        required.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        required.append(secrets.choice(string.digits))
    if use_symbols:
        required.append(secrets.choice(SYMBOLS))

    if len(required) > length:
        return "Недостаточная длина для выбранных типов"

    remaining = length - len(required)
    password_chars = required + [secrets.choice(alphabet) for _ in range(remaining)]

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


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
        self.setWindowTitle("Генератор паролей | PySide6")
        self.setFixedSize(450, 500)

        layout = QVBoxLayout()

        # Выбор темы
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Тема:")
        self.theme_box = QComboBox()
        self.theme_box.addItems(["Светлая", "Темная"])
        self.theme_box.currentIndexChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_box)
        layout.addLayout(theme_layout)

        # Ползунок длины
        length_label = QLabel("Длина пароля: 16")
        self.length_label = length_label
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(8)
        slider.setMaximum(32)
        slider.setValue(16)
        slider.valueChanged.connect(lambda v: self.length_label.setText(f"Длина пароля: {v}"))
        self.length_slider = slider

        layout.addWidget(length_label)
        layout.addWidget(slider)

        # Чекбоксы
        self.cb_lower = QCheckBox("Строчные (a-z)")
        self.cb_upper = QCheckBox("Заглавные (A-Z)")
        self.cb_digits = QCheckBox("Цифры (0-9)")
        self.cb_symbols = QCheckBox("Спецсимволы (!@#…)")
        for cb in (self.cb_lower, self.cb_upper, self.cb_digits, self.cb_symbols):
            cb.setChecked(True)
            layout.addWidget(cb)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Сгенерировать один пароль")
        self.generate_many_btn = QPushButton("Сгенерировать 10 паролей")
        self.generate_btn.clicked.connect(self.generate_one)
        self.generate_many_btn.clicked.connect(self.generate_many)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.generate_many_btn)
        layout.addLayout(btn_layout)

        # Поле вывода одного пароля
        self.output = QLineEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # Копировать
        self.copy_btn = QPushButton("Копировать пароль")
        self.copy_btn.clicked.connect(self.copy_pwd)
        layout.addWidget(self.copy_btn)

        # Индикатор сложности
        self.strength_label = QLabel("Сложность: –")
        layout.addWidget(self.strength_label)

        # Вывод нескольких паролей
        self.multi_output = QTextEdit()
        self.multi_output.setReadOnly(True)
        layout.addWidget(self.multi_output)

        self.setLayout(layout)
        self.apply_theme()

    def get_flags(self):
        return (
            self.length_slider.value(),
            self.cb_lower.isChecked(),
            self.cb_upper.isChecked(),
            self.cb_digits.isChecked(),
            self.cb_symbols.isChecked()
        )

    def generate_one(self):
        length, lo, up, dg, sy = self.get_flags()
        pwd = generate_password(length, lo, up, dg, sy)
        self.output.setText(pwd)
        self.strength_label.setText(f"Сложность: {rate_strength(pwd)}")

    def generate_many(self):
        length, lo, up, dg, sy = self.get_flags()
        self.multi_output.clear()
        for _ in range(10):
            pwd = generate_password(length, lo, up, dg, sy)
            self.multi_output.append(pwd)

    def copy_pwd(self):
        QApplication.clipboard().setText(self.output.text())

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