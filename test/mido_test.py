from mido import MidiFile

# Lade die MIDI-Datei
midi_path = r"D:\creativechoon\generated_midi.mid"
midi_file = MidiFile(midi_path)

# Analysiere den Inhalt der MIDI-Datei
for i, track in enumerate(midi_file.tracks):
    print(f'Track {i}: {track.name}')
    for msg in track:
        print(msg)
