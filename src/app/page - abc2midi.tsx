'use client';

import React, { useState } from 'react';

export default function Home() {
    const [userInput, setUserInput] = useState('');
    const [bars, setBars] = useState('4');
    const [compositionType, setCompositionType] = useState('melody');
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
            }),
        });

        if (response.ok) {
            const data = await response.json();
            setModelResponse(data.modelResponse);

            // Hier wird der Base64-String dekodiert
            const byteCharacters = atob(data.midiFile);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const midiBlob = new Blob([byteArray], { type: 'audio/midi' });

            const url = window.URL.createObjectURL(midiBlob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'generated_midi.mid');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            console.error('Failed to generate MIDI file');
            setModelResponse("Fehler beim Generieren der MIDI-Datei.");
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

            <button onClick={handleGenerate} style={styles.button}>generate</button>

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
