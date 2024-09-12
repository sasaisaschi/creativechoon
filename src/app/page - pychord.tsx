'use client';

import React, { useState } from 'react';

export default function Home() {
    const [userInput, setUserInput] = useState('');
    const [bars, setBars] = useState('4');
    const [compositionType, setCompositionType] = useState('melody');
    const [bpm, setBpm] = useState('75');
    const [octave, setOctave] = useState('3');
    const [humanize, setHumanize] = useState(false);
    const [modelResponse, setModelResponse] = useState('');

    const handleGenerate = async () => {
        const response = await fetch('http://localhost:5000/api/generate_midi', {
            method: 'POST',
            mode: 'cors',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: userInput,
                bars: bars,
                compositionType: compositionType,
                bpm: bpm,
                octave: octave,
                humanize: humanize
            }),
        });

        if (response.ok) {
            const data = await response.json();
            setModelResponse(data.modelResponse);

            // Hier wird die MIDI-Datei heruntergeladen
            if (data.midiFile) {
                const byteCharacters = atob(data.midiFile);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const midiBlob = new Blob([byteArray], { type: 'audio/midi' });

                const url = window.URL.createObjectURL(midiBlob);

                // Verwende den Dateinamen, der vom Backend zurückgegeben wurde
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', data.filename); // hier wird der korrekte Dateiname verwendet
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        } else {
            const errorData = await response.json();
            setModelResponse("Fehler: " + errorData.error + "\nModellantwort: " + (errorData.modelResponse || "") + "\nDetails: " + (errorData.details || ""));
        }
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.title}>CreativeChoon</h1>

            <label style={styles.label} htmlFor="mood-input">
                Stimmung, Lieblingskünstler oder Komponist:
                <input
                    id="mood-input"
                    name="mood"
                    type="text"
                    placeholder="Enter mood, favorite artist, etc."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    style={styles.input}
                />
            </label>

            <label style={styles.label} htmlFor="bars-select">
                Taktanzahl:
                <select id="bars-select" name="bars" value={bars} onChange={(e) => setBars(e.target.value)} style={styles.select}>
                    <option value="4">4 bars</option>
                    <option value="8">8 bars</option>
                    <option value="16">16 bars</option>
                    <option value="32">32 bars</option>
                </select>
            </label>

            <label style={styles.label} htmlFor="composition-select">
                Art der Komposition:
                <select id="composition-select" name="compositionType" value={compositionType} onChange={(e) => setCompositionType(e.target.value)} style={styles.select}>
                    <option value="melody">melody</option>
                    <option value="chord">chord</option>
                </select>
            </label>

            <label style={styles.label} htmlFor="bpm-input">
                BPM:
                <input
                    id="bpm-input"
                    name="bpm"
                    type="number"
                    placeholder="Enter BPM"
                    value={bpm}
                    onChange={(e) => setBpm(e.target.value)}
                    style={styles.input}
                />
            </label>

            <label style={styles.label} htmlFor="octave-input">
                Oktave:
                <input
                    id="octave-input"
                    name="octave"
                    type="number"
                    placeholder="Enter Octave"
                    value={octave}
                    onChange={(e) => setOctave(e.target.value)}
                    style={styles.input}
                />
            </label>

            <label style={styles.label} htmlFor="humanize-input">
                Humanize:
                <input
                    id="humanize-input"
                    name="humanize"
                    type="checkbox"
                    checked={humanize}
                    onChange={(e) => setHumanize(e.target.checked)}
                    style={styles.checkbox}
                />
            </label>

            <button onClick={handleGenerate} style={styles.button}>Generate</button>

            <div style={styles.responseContainer}>
                <h2>Modellantwort:</h2>
                <textarea value={modelResponse} readOnly style={styles.textarea}></textarea>
            </div>
        </div>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        textAlign: 'center',
    },
    title: {
        marginBottom: '20px',
        fontSize: '2em',
        color: '#333',
    },
    label: {
        marginBottom: '10px',
        fontSize: '1.2em',
        color: '#555',
    },
    input: {
        padding: '10px',
        fontSize: '1em',
        width: '300px',
        marginTop: '5px',
    },
    select: {
        padding: '10px',
        fontSize: '1em',
        width: '320px',
        marginTop: '5px',
    },
    checkbox: {
        marginLeft: '10px',
    },
    button: {
        padding: '10px 20px',
        fontSize: '1.2em',
        color: '#fff',
        backgroundColor: '#007BFF',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        marginTop: '20px',
    },
    responseContainer: {
        marginTop: '20px',
        width: '100%',
        maxWidth: '500px',
    },
    textarea: {
        width: '100%',
        height: '150px',
        fontSize: '1em',
        padding: '10px',
    },
};
