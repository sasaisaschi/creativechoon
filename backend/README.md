# CreativeChoon Backend

## Einleitung

Das Backend von **CreativeChoon** ist eine leistungsfähige API, die MIDI-Dateien basierend auf Benutzereingaben generiert. Es verwendet FastAPI als Web-Framework und integriert die Groq API sowie das Llama 3 Model zur Verarbeitung und Interpretation von Benutzereingaben. Dieses Backend ist dafür verantwortlich, die musikalischen Parameter aus den Eingaben zu extrahieren und die entsprechenden MIDI-Dateien zu erstellen.

## Inhaltsverzeichnis

1. [Einleitung](#einleitung)
2. [Technologien](#technologien)
3. [Installation](#installation)
   - [Voraussetzungen](#voraussetzungen)
   - [Installation der Abhängigkeiten](#installation-der-abhängigkeiten)
   - [Starten des Servers](#starten-des-servers)
4. [Verwendung](#verwendung)
5. [API-Endpunkte](#api-endpunkte)
6. [Ordnerstruktur](#ordnerstruktur)
7. [Lizenz](#lizenz)

## Technologien

- **FastAPI**: Ein modernes, schnelles Web-Framework für den Aufbau von APIs mit Python.
- **Groq API**: Ermöglicht den Zugriff auf leistungsstarke AI-Modelle wie Llama 3.
- **LlamaAPI**: SDK für die einfache Interaktion mit dem Llama 3 Model.
- **Mido & python-rtmidi**: Bibliotheken zur Erstellung und Bearbeitung von MIDI-Dateien.

## Installation

### Voraussetzungen

Stelle sicher, dass folgende Software auf deinem System installiert ist:

- **Python 3.8+**
- **pip** (Python Paketmanager)

### Installation der Abhängigkeiten

1. Klone das Repository:

    ```bash
    git clone https://github.com/DEIN_GITHUB_USERNAME/CreativeChoon.git
    cd CreativeChoon/backend
    ```

2. Erstelle und aktiviere eine virtuelle Umgebung:

    ```bash
    python3 -m venv env
    source env/bin/activate  # Auf Windows: env\Scripts\activate
    ```

3. Installiere die Abhängigkeiten:

    ```bash
    pip install -r requirements.txt
    ```

### Starten des Servers

1. Stelle sicher, dass die Umgebung aktiviert ist.
2. Starte den FastAPI-Server mit Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

3. Der Server wird standardmäßig unter [http://localhost:8000](http://localhost:8000) laufen.

## Verwendung

Nach dem Starten des Servers kannst du über die API Endpunkte MIDI-Dateien generieren lassen. Nutze dafür Tools wie `curl`, Postman oder eine Frontend-Anwendung, um HTTP-Anfragen zu stellen.

## API-Endpunkte

- **`POST /generate_midi/`**: Generiert eine MIDI-Datei basierend auf den übermittelten Benutzereingaben.
  - **Body**: JSON-Objekt mit einem Textfeld `input`, das die Stimmung, Lieblingskünstler oder andere Parameter enthält.
  - **Response**: Statusmeldung und Details der generierten MIDI-Datei.

## Ordnerstruktur

```plaintext
backend/
├── app/                # FastAPI-Anwendung
├── main.py             # Einstiegspunkt für FastAPI
├── requirements.txt    # Abhängigkeiten
└── output/             # Generierte MIDI-Dateien
