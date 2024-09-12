import os
import subprocess
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import tempfile

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = Groq(api_key=GROQ_API_KEY)


def abc_to_midi(abc_code):
    """Konvertiert ABC-Notation in eine MIDI-Datei."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".abc") as abc_file:
            abc_fp = abc_file.name
            abc_file.write(abc_code.encode('utf-8'))

        midi_fp = abc_fp.replace(".abc", ".mid")

        # Konvertiere ABC zu MIDI mit abc2midi
        subprocess.run(["abc2midi", abc_fp, "-o", midi_fp], check=True)

        with open(midi_fp, "rb") as f:
            midi_data = f.read()

        os.remove(abc_fp)
        os.remove(midi_fp)

        # Base64-Kodierung des MIDI-Byte-Arrays
        return base64.b64encode(midi_data).decode('utf-8')

    except Exception as e:
        print(f"Error converting ABC to MIDI: {str(e)}")
        raise


def correct_abc_notation(model_response):
    """Korrigiert die ABC-Notation, um sicherzustellen, dass sie korrekt interpretiert werden kann."""
    corrected_abc = "X:1\nT:Epic Sorrow\nM:4/4\nL:1/4\nK:Cmin\n"
    corrected_abc += model_response.replace('|', '|\n')  # Korrigiere die Akkordnotation
    return corrected_abc


@app.route("/api/generate_midi", methods=["POST"])
def generate_midi():
    data = request.json
    user_input = data.get("input", "")
    composition_type = data.get("compositionType", "melody")

    print(f"Received input: {user_input}")
    print(f"Received compositionType: {composition_type}")

    if not user_input:
        return jsonify({"error": "User input is required"}), 400

    # Klar definierter Prompt für Akkorde
    prompt_content = (
        "You are a music composition assistant. Your task is to generate a chord progression in ABC notation. "
        "Please generate only chords using ABC notation like '[C,E,G]'. Do not include any melodies, comments, or explanations."
    ) if composition_type == "chord" else (
        "You are a music composition assistant. Your task is to generate a melody in ABC notation. "
        "Please generate a melody without any chords or explanations."
    )

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": prompt_content},
            {"role": "user", "content": f"{user_input}, {composition_type}"}
        ],
        temperature=1,
        max_tokens=8192,
        top_p=1,
        stream=False,
        stop=None,
    )

    model_response = completion.choices[0].message.content
    print(f"Model response: {model_response}")

    # Filtere die Rückgabe, um nur gültige ABC-Notation zu behalten
    corrected_response = correct_abc_notation(model_response)

    # Konvertiere in MIDI
    try:
        midi_data = abc_to_midi(corrected_response)
    except Exception as e:
        return jsonify({"error": f"Failed to convert ABC to MIDI: {str(e)}"}), 500

    return jsonify({
        "midiFile": midi_data,
        "modelResponse": corrected_response
    })

if __name__ == "__main__":
    app.run(debug=True)
