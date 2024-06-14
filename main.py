import sys
import mido
from consts import *
from converter import Converter

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.converter = Converter()
        self.file_name = None

        self.channel_sounds = {}
        self.setupUi(self)
        self.btn_load_file.clicked.connect(self.open_file)
        self.btn_convert.clicked.connect(self.convert)
        self.rb_channel.pressed.connect(self.change_mode)
        self.rb_note.pressed.connect(self.change_mode)
        self.rb_random.pressed.connect(self.change_mode)

    def change_mode(self):
        modes = {
            self.rb_channel: SOUND_FROM_CHANNEL,
            self.rb_note: SOUND_FROM_SETUP,
            self.rb_random: RANDOM_SOUND
        }
        self.converter.set_mode(modes.get(self.sender()))

    def open_file(self):
        self.file_name = QFileDialog.getOpenFileName(self, 'Выбор файла', '')[0]

        midi_file = mido.MidiFile(self.file_name)
        channels = set()
        for msg in midi_file:
            channel = msg.__dict__.get('channel')
            if msg.type == 'note_on' and channel is not None:
                channels.add(channel)

        for _ in range(self.channel_layout.rowCount()):
            self.channel_layout.removeRow(0)
        for channel in sorted(channels):
            channel_combo_box = ChannelComboBox(self, channel)
            self.channel_layout.addRow(f'channel {channel + 1}', channel_combo_box)
            channel_combo_box.currentTextChanged.connect(self.update_channel_sounds)
            self.channel_sounds[channel] = SOUNDS.get(channel_combo_box.currentText())

    def update_channel_sounds(self):
        channel = self.sender().channel
        sound_name = self.sender().currentText()
        self.channel_sounds[channel] = SOUNDS.get(sound_name)
        self.converter.set_channel_sounds(self.channel_sounds)

    def convert(self):
        self.converter.convert(self.file_name)


class ChannelComboBox(QComboBox):
    def __init__(self, parent, channel):
        super().__init__(parent)
        self.setIconSize(QSize(56, 56))
        self.channel = channel
        if channel == 9:
            self.setEnabled(False)
            self.addItem('Барабаны')
        else:
            for sound_name in ICONS:
                self.addItem(QIcon(ICONS.get(sound_name)), sound_name)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
