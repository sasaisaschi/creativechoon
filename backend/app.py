from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import random
import os
import io
import base64
from datetime import datetime
from pychord import Chord
import librosa
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from groq import Groq

# Laden der Umgebungsvariablen
load_dotenv()

# Flask App erstellen
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

# Groq API Key aus den Umgebungsvariablen laden
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

# Groq Client initialisieren
client = Groq(api_key=GROQ_API_KEY)

# Relativer Output-Pfad zum Projektverzeichnis
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Stelle sicher, dass der Output-Ordner existiert
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_keynote(generated_text):
    """Extrahiert die Tonart aus dem generierten Text."""
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

    if not user_input:
        return jsonify({"error": "User input is required"}), 400

    prompt_content = (
        f"Generate a {composition_type} based on the user's mood or input: '{user_input}', "
        f"over {bars} bars. Please do not add further explanations."
    )

    try:
        # Modellaufruf für Generierung
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

        generated_text = completion.choices[0].message.content.strip()
        keynote = extract_keynote(generated_text)

        # MIDI-Datei basierend auf Typ generieren
        if composition_type == "melody":
            midi_data = generate_midi_from_melody(generated_text, bpm, octave, humanize)
        else:
            chords_text = generated_text.replace(" - ", " ").replace("-", " ").replace("  ", " ")
            midi_data = generate_midi_from_chords(chords_text, bpm, octave, humanize)

        if midi_data:
            filename = f"{keynote}_{bpm}bpm_{composition_type}_{bars}bars_{datetime.now().strftime('%Y%m%d')}.mid"
            output_path = os.path.join(OUTPUT_DIR, filename)

            # MIDI-Datei speichern
            with open(output_path, 'wb') as f:
                f.write(midi_data)

            encoded_midi = base64.b64encode(midi_data).decode('utf-8')
            return jsonify({"modelResponse": generated_text, "midiFile": encoded_midi, "filename": filename}), 200
        else:
            return jsonify({"error": "MIDI file was not created properly", "modelResponse": generated_text}), 500

    except Exception as e:
        return jsonify({"error": "Model generation failed", "details": str(e)}), 500

def generate_midi_from_chords(chords_string, bpm, octave, humanize):
    """Generiert MIDI-Daten aus einer Chord-Sequenz."""
    chords = chords_string.split()
    midi_chords = []
    for word in chords:
        try:
            chord = Chord(word)
            notes = chord.components_with_pitch(root_pitch=octave)
            midi_chords.append([librosa.note_to_midi(note) for note in notes])
        except Exception:
            continue

    if not midi_chords:
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
        velocity = random.randrange(64, 84)
        start = 0 if not humanize else random.randint(0, humanization_amount)
        for note in chord:
            if 0 <= note <= 127:
                track.append(Message('note_on', note=int(note), velocity=velocity, time=start))
        for note in chord:
            if 0 <= note <= 127:
                track.append(Message('note_off', note=int(note), velocity=velocity, time=bar))

    midi_bytes = io.BytesIO()
    mid.save(file=midi_bytes)
    midi_bytes.seek(0)
    return midi_bytes.read()

def generate_midi_from_melody(melody_string, bpm, octave, humanize):
    """Generiert MIDI-Daten aus einer Melodie-Sequenz."""
    notes = melody_string.split()
    midi_notes = []
    for word in notes:
        try:
            note_name, note_octave = word[:-1], word[-1]
            midi_note = librosa.note_to_midi(note_name + note_octave)
            midi_notes.append(midi_note)
        except Exception:
            continue

    if not midi_notes:
        raise ValueError("No valid notes to generate MIDI from.")

    tpb = 128
    note_duration = tpb
    humanization_amount = 9

    mid = MidiFile(ticks_per_beat=tpb)
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    for i, note in enumerate(midi_notes, 1):
        if 0 <= note <= 127:
            velocity = random.randrange(64, 84)
            start = 0 if not humanize else random.randint(0, humanization_amount)
            track.append(Message('note_on', note=int(note), velocity=velocity, time=start))
            track.append(Message('note_off', note=int(note), velocity=velocity, time=note_duration))

    midi_bytes = io.BytesIO()
    mid.save(file=midi_bytes)
    midi_bytes.seek(0)
    return midi_bytes.read()

# Flask Server starten
if __name__ == '__main__':
    app.run(debug=True)
