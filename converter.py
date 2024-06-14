import mido
from consts import *
from random import choice


class Converter:
    def __init__(self, sound=None):
        self.sound = sound
        if sound is None:
            self.set_random_sound()
        self.offset = NOTES_OFFSET.get(sound, 66)
        self.prev_speed = None
        self.mode = SOUND_FROM_SETUP
        self.sounds_from_setup = {
            'default': self.sound
        }
        self.channel_sounds = {
            0: '_pause', 1: '_pause', 2: '_pause', 3: '_pause', 4: '_pause', 5: '_pause', 6: '_pause', 7: '_pause',
            8: '_pause', 9: '_pause', 10: '_pause', 12: '_pause', 13: '_pause', 14: '_pause', 15: '_pause'
        }

    def set_mode(self, mode):
        self.mode = mode

    def set_sound_setup(self, setup):
        self.sounds_from_setup = setup

    def set_channel_sounds(self, channel_sounds):
        self.channel_sounds = channel_sounds

    def set_sound_from_note(self, note):
        for key in self.sounds_from_setup:
            if isinstance(key, int):
                if note == key:
                    self.set_sound(self.sounds_from_setup.get(key))
                    return
            elif isinstance(key, tuple):
                x, y = key
                if x <= note < y:
                    self.set_sound(self.sounds_from_setup.get(key))
                    return
        self.set_sound(self.sounds_from_setup.get('default'))

    def set_sound_from_channel(self, channel):
        self.sound = self.channel_sounds.get(channel)

    def set_random_sound(self):
        self.set_sound(choice(list(NOTES_OFFSET.keys())))

    def set_sound(self, sound):
        self.sound = sound
        self.offset = NOTES_OFFSET.get(sound, 66)

    def convert(self, midi_file_name):
        midi_file = mido.MidiFile(midi_file_name)
        result = []
        chord = []
        self.prev_speed = None
        prev_not_chord = True
        time = 0
        for msg in midi_file:
            channel = msg.__dict__.get('channel')
            if msg.type == 'note_on':
                if self.mode == SOUND_FROM_SETUP:
                    self.set_sound_from_note(msg.note)
                elif self.mode == SOUND_FROM_CHANNEL:
                    self.set_sound_from_channel(channel)
                elif self.mode == RANDOM_SOUND:
                    self.set_random_sound()
                if msg.time:
                    prev_not_chord = True
                time += msg.time
                if prev_not_chord:
                    self.add_pause_to_result(time, result)
                    self.add_chord_to_result(chord, result)
                time = 0
                if channel == 9:
                    self.add_drum_note_to_chord(msg.note, chord)
                else:
                    self.add_note_to_chord(msg.note, chord)
                prev_not_chord = False
            elif msg.time:
                prev_not_chord = True
                time += msg.time
        if chord:
            self.add_pause_to_result(time, result)
            self.add_chord_to_result(chord, result)
        with open('output.txt', 'w', encoding='utf-8') as output:
            output.write('|'.join(result))

    def add_note_to_chord(self, note, chord):
        chord.append(f'{self.sound}@{note - self.offset}')

    def add_drum_note_to_chord(self, note, chord):
        chord.append(f'{DRUM_NOTES.get(note)}')

    def add_chord_to_result(self, chord, result):
        result.append(f'{"|!combine|".join(chord)}')
        chord.clear()

    def add_pause_to_result(self, time, result):
        if time:
            speed = f'{60 / time:0.3f}'
            if speed != self.prev_speed:
                result.append(f'!speed@{speed}')
                self.prev_speed = speed


if __name__ == '__main__':
    converter = Converter()
    converter.convert('midi/test4.mid')
