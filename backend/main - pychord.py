from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os
import io
import base64
import re
from datetime import datetime
from pychord import Chord
import librosa
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = Groq(api_key=GROQ_API_KEY)

def extract_keynote(generated_text):
    # Annahme: Die Keynote ist das erste Wort im generierten Text (Note oder Akkord)
    return generated_text.split()[0]

@app.route("/api/generate_midi", methods=["POST"])
def generate_midi():
    data = request.json
    user_input = data.get("input", "")
    composition_type = data.get("compositionType", "melody")
    bars = int(data.get("bars", 4))
    bpm = int(data.get("bpm", 75))
    octave = int(data.get("octave", 3))
    humanize = bool(data.get("humanize", False))

    print(f"Received input: {user_input}")
    print(f"Received bars: {bars}")
    print(f"Received compositionType: {composition_type}")
    print(f"Received BPM: {bpm}")
    print(f"Received Octave: {octave}")
    print(f"Received Humanize: {humanize}")

    if not user_input:
        return jsonify({"error": "User input is required"}), 400

    # System-Prompt für das Modell
    prompt_content = (
        f"Generate a {composition_type} based on the user's mood or input: '{user_input}', "
        f"over {bars} bars. Please do not add further explanations."
    )

    # Model-API-Aufruf
    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {"role": "system", "content": prompt_content},
                {"role": "user", "content": f"{user_input}, {bars}, {composition_type}"}
            ],
            temperature=1,
            max_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Zugriff auf den generierten Text
        generated_text = completion.choices[0].message.content.strip()
        print(f"Generated text: {generated_text}")

        # Ermittlung der Keynote
        keynote = extract_keynote(generated_text)

        # Prüfen, welcher Typ von Komposition generiert werden soll
        if composition_type == "melody":
            midi_data = generate_midi_from_melody(generated_text, bpm, octave, humanize)
        else:
            # Entfernen der Bindestriche und doppelten Leerzeichen für Akkorde
            chords_text = generated_text.replace(" - ", " ").replace("-", " ").replace("  ", " ")
            midi_data = generate_midi_from_chords(chords_text, bpm, octave, humanize)

        # Überprüfen, ob die MIDI-Daten vorhanden sind
        if midi_data:
            encoded_midi = base64.b64encode(midi_data).decode('utf-8')

            # Generierung des Dateinamens basierend auf den Parametern
            filename = f"{keynote}_{bpm}bpm_{composition_type}_{bars}bars_{datetime.now().strftime('%Y%m%d')}.mid"
            print(f"Generated filename: {filename}")

            return jsonify({"modelResponse": generated_text, "midiFile": encoded_midi, "filename": filename}), 200
        else:
            return jsonify({"error": "MIDI file was not created properly", "modelResponse": generated_text}), 500

    except Exception as e:
        return jsonify({"error": "Model generation failed", "details": str(e)}), 500

def generate_midi_from_chords(chords_string, bpm, octave, humanize):
    chords = chords_string.split()

    midi_chords = []
    for word in chords:
        if word:
            try:
                chord = Chord(word)
                notes = chord.components_with_pitch(root_pitch=octave)
                midi_chords.append([librosa.note_to_midi(note) for note in notes])
            except Exception as e:
                print(f"Failed to parse chord {word}: {str(e)}")
                continue

    if not midi_chords:
        print("No MIDI chords were generated, aborting.")
        raise ValueError("No valid chords to generate MIDI from.")

    tpb = 128
    bar = tpb
    humanization_amount = 9

    mid = MidiFile(ticks_per_beat=tpb)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    for chord in midi_chords:
        velocity = random.randrange(64, 84) if 64 != 84 else 84
        start = 0 if not humanize else random.randint(0, humanization_amount)
        # Noten gleichzeitig spielen lassen
        for note in chord:
            if 0 <= note <= 127:  # Validierung des Notenbereichs
                track.append(Message('note_on', note=int(note), velocity=velocity, time=start))
        for note in chord:
            if 0 <= note <= 127:  # Validierung des Notenbereichs
                track.append(Message('note_off', note=int(note), velocity=velocity, time=bar))

    midi_bytes = io.BytesIO()
    mid.save(file=midi_bytes)
    midi_bytes.seek(0)
    return midi_bytes.read()

def generate_midi_from_melody(melody_string, bpm, octave, humanize):
    notes = melody_string.split()

    midi_notes = []
    for word in notes:
        try:
            note_name, note_octave = word[:-1], word[-1]
            midi_note = librosa.note_to_midi(note_name + note_octave)
            midi_notes.append(midi_note)
        except Exception as e:
            print(f"Failed to parse note {word}: {str(e)}")
            continue

    if not midi_notes:
        print("No MIDI notes were generated, aborting.")
        raise ValueError("No valid notes to generate MIDI from.")

    tpb = 128  # Höhere Tickrate für feinere Notenplatzierung
    note_duration = tpb  # Noten werden für eine halbe Taktlänge gehalten
    humanization_amount = 9

    mid = MidiFile(ticks_per_beat=tpb)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    for i, note in enumerate(midi_notes, 1):
        if 0 <= note <= 127:  # Validierung des Notenbereichs
            velocity = random.randrange(64, 84) if 64 != 84 else 84
            start = 0 if not humanize else random.randint(0, humanization_amount)
            track.append(Message('note_on', note=int(note), velocity=velocity, time=start))
            track.append(Message('note_off', note=int(note), velocity=velocity, time=note_duration))
        else:
            print(f"Note {note} out of range, skipping.")

    midi_bytes = io.BytesIO()
    mid.save(file=midi_bytes)
    midi_bytes.seek(0)
    return midi_bytes.read()

if __name__ == '__main__':
    app.run(debug=True)
