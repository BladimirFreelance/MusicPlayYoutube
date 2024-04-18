import os
import sys
import vlc
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QCoreApplication
from yt_dlp import YoutubeDL
import requests

# Функция для проверки интернет-соединения
def check_internet_connection():
    try:
        requests.get('http://www.google.com', timeout=3)
        return True
    except requests.exceptions.RequestException:
        return False

# Функция для определения текущего пути к ресурсам
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class VolumeControlWidget(QtWidgets.QWidget):
    def __init__(self, player):
        super().__init__(flags=QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.player = player
        self.initUI()

    def initUI(self):
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setRange(0, 100)  # Диапазон громкости от 0 до 100
        self.slider.setValue(self.player.audio_get_volume())
        self.slider.valueChanged.connect(self.set_volume)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.slider)
        self.setLayout(layout)
        self.setWindowTitle('Регулировка громкости')

    def set_volume(self, value):
        self.player.audio_set_volume(value)

class SystemTrayApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.player = vlc.MediaPlayer()
        self.initTrayIcon()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_connection_status)
        self.timer.start(3500)  # Проверка соединения каждые 10 секунд
        self.is_playing = False

    def initTrayIcon(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon_path = resource_path("YourIcon.png") # измените YourIcon.png на имя вашего файла, он должен находитмя в каталоге где находится ваш main.py

        quit_action = QtWidgets.QAction("Exit", self)
        quit_action.triggered.connect(QCoreApplication.instance().quit)
        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.tray_icon.setIcon(QtGui.QIcon(icon_path))
        self.tray_icon.setToolTip("MusicPlayYoutube")
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # Проверяем, что была нажата левая кнопка мыши
            self.show_volume_control()

    def show_volume_control(self):
        # Убедитесь, что этот метод определен в вашем классе и корректно отображает виджет регулировки громкости
        if not hasattr(self, 'volume_control_widget'):
            self.volume_control_widget = VolumeControlWidget(self.player)
            self.volume_control_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.volume_control_widget.show()
        self.volume_control_widget.raise_()
        self.volume_control_widget.activateWindow()


    def update_connection_status(self):
        if check_internet_connection():
            if not self.is_playing:
                self.play_youtube_live(self.current_url)
                self.tray_icon.setToolTip("MusicPlayYoutube")
        else:
            if self.is_playing:
                self.player.stop()
                self.is_playing = False
            self.tray_icon.setToolTip("Интернет отключен")

    def play_youtube_live(self, url):
        self.current_url = url
        with YoutubeDL({'format': 'bestaudio'}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            audio_url = info_dict.get('url', None)
        if audio_url:
            self.player.set_media(vlc.Media(audio_url))
            self.player.play()
            self.is_playing = True
        else:
            self.is_playing = False

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = SystemTrayApp()
    w.hide()
    youtube_live_url = "https://www.youtube.com/live/Your URL Yotube Live Music"
    w.play_youtube_live(youtube_live_url)
    sys.exit(app.exec_())
