#!/usr/env python3
"""
klungo sing 4 u...
spoocecow 2026
"""

import os

import subprocess
import tempfile
from pathlib import Path

import funmid
import midi2vox

# map a time to a single note
FlatNotes = dict[int, funmid.MidiNote]

tts = ['espeak', '-s', '60']
pitcher = 'rubberband-r3'

TOY = '/home/mark/Music/midis/cavestory/Cave_Story_-_Balrogs_Theme.mid'
TOY = '/home/mark/Music/midis/Bbtitle2.mid'

def extract_midi(midi_fn:str=TOY) -> funmid.SimplyNotes:
    midi = funmid.MidiFile(midi_fn)
    return midi.to_simplynotes()

def extract_midi_track(midi:funmid.SimplyNotes, track:int=1) -> tuple[funmid.Notes, int]:
    # roughly follow what midi2vox.crunch does to get a simple list of notes and rests
    track = midi.by_track()[track]
    final_notes = [n for n in track if n.what == funmid.MidiNote.NOTE_ON]
    better = midi.copy(notes=final_notes)
    flattened = {}
    for t, notes in sorted(better.by_time().items()):
        if len(notes) > 1:
            note = midi2vox.get_chord_root(notes)
        else:
            note = notes[0]
        flattened[t] = note

    # do some sanity checkin'
    tick_quantize = midi.ticks_per_beat / 4
    min_note_length = int(4 * (midi.ticks_per_beat / tick_quantize))
    default_bpm = midi.bpm()
    if min_note_length > 32:
        default_bpm = int(midi.bpm() * (min_note_length / 32))
        min_note_length = 32
        print("Notes are too short, increasing bpm to {bpm}".format(bpm=default_bpm))
    if default_bpm > 300:
        tick_quantize = int(tick_quantize * (midi.bpm() / 300))
        default_bpm = 300
        print("BPM too high, increasing tick quantization to {q}".format(q=tick_quantize))
    print(f"tick_quantize: {tick_quantize}")
    min_note_length = int(4 * (midi.ticks_per_beat / tick_quantize))
    return midi2vox.quantize_to_beat(flattened, tick_quantize), tick_quantize

"Ball rog time ball rog time every day is ball rog time"

def main(line:str="doo "*16, final_fn:str='/tmp/balrogtime.wav', midi_fn:str=TOY, track:int=1):
    midi = extract_midi(midi_fn)
    print(midi)
    notes, tick_q = extract_midi_track(midi, track)
    print("\n" + '@'*40)
    L = len(line.split())
    for note in notes:
        if isinstance(note, midi2vox.LengthChange):
            continue
        print(note)
        L -= 1
        if not L:
            break
    print("\n" + '@'*40)
    #return notes
    d = '/tmp/midifun'
    if True:
    #with tempfile.TemporaryDirectory() as d:

        # chop up line into word wavs
        wavs = []
        for i, word in enumerate(line.split()):
            fn = Path(d) / f'raw_{i:03}.wav'
            if subprocess.run(['espeak', '-z', '-s', '60', '-w', fn, word]).returncode == 0:
                wavs.append(fn)

        # now, map each word to each note's pitch and length
        bpm = midi.bpm()
        print(f"bpm = {bpm}, tick_q = {tick_q}, ticks_per_beat = {midi.ticks_per_beat}")
        stretchfactor = 2
        middle_c = 60
        noter = iter(notes)
        finals = []
        try:
            for wordwav in wavs:
                note = next(noter)
                while isinstance(note, midi2vox.LengthChange):
                    if note.what == midi2vox.LengthChange.INC:
                        stretchfactor /= 2
                    elif note.what == midi2vox.LengthChange.DEC:
                        stretchfactor *= 2
                    note = next(noter)

                pitch = note.note

                print(f"Resolved stretchfactor: {stretchfactor}")

                # TODO
                #stretchfactor = 1

                if note.is_rest():
                    #note = next(noter)
                    wordwav = '/home/mark/blank.wav'
                    pitch = middle_c

                whole_note_len = bpm
                dur_ticks = note.dur  # TODO use rubberband time ratio? what's a whole note/quarter note/etc dur again...?
                dur_s = (dur_ticks / midi.ticks_per_beat)*(60/bpm)
                print(note, str(wordwav), midi.ticks_per_beat)
                print(f"A beat should be {60/bpm}s right? so this note ({dur_ticks} ticks, {dur_ticks/midi.ticks_per_beat} beats) should be {dur_s}s long...?")
                out_fn = str(wordwav).replace('raw', 'good')
                #args = ['rubberband-r3', '--duration', str(dur_s),  '-F', '-p', str(pitch-middle_c), str(wordwav), out_fn]

                semitones_adj = (pitch - middle_c) * 2

                args = ['rubberband-r3', '-F', '--tempo', f'60:{bpm/(stretchfactor)}', '-p', str(semitones_adj), str(wordwav), out_fn]
                print(args)
                subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                finals.append(out_fn)
        except StopIteration:
            print("ran outta words")
        if finals:
            args = ['sox', *finals, final_fn]
            print(args)
            subprocess.run(args)
    print("Done")

if __name__ == "__main__":
    main()