import mido
from consts import *
from random import choice


class Converter:
    def __init__(self, sound=None):
        if sound is None:
            self.set_random_sound()
        self.sound = sound
        self.offset = NOTES_OFFSET.get(sound, 66)
        self.prev_speed = None
        self.mode = NOTE_FROM_SETUP
        self.notes = {
            'default': self.sound
        }

    def set_mode(self, mode):
        self.mode = mode

    def set_notes_setup(self, setup):
        self.notes = setup

    def set_sound_from_note(self, note):
        for key in self.notes:
            if isinstance(key, int):
                if note == key:
                    self.set_sound(self.notes.get(key))
                    return
            elif isinstance(key, tuple):
                x, y = key
                if x <= note < y:
                    self.set_sound(self.notes.get(key))
                    return
        self.set_sound(self.notes.get('default'))

    def set_random_sound(self):
        self.set_sound(choice(list(NOTES_OFFSET.keys())))

    def set_sound(self, sound):
        self.sound = sound
        self.offset = NOTES_OFFSET.get(sound, 66)

    def convert(self, midi_file_name):
        midi_file = mido.MidiFile('midi/' + midi_file_name)
        result = []
        chord = []
        self.prev_speed = None
        prev_not_chord = True
        time = 0
        for msg in midi_file:
            channel = msg.__dict__.get('channel')
            if msg.type == 'note_on':
                self.set_sound_from_note(msg.note)
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
    converter.set_notes_setup(MINECRAFT1_SETUP)
    converter.convert(
        "Rimsky Korsakov ''Flight Of the Bumblebee''.mid"
    )
