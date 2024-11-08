'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send } from 'lucide-react';

export default function Home() {
    const [userInput, setUserInput] = useState('');
    const [bars, setBars] = useState('4');
    const [compositionType, setCompositionType] = useState('melody');
    const [bpm, setBpm] = useState('75');
    const [octave, setOctave] = useState('3');
    const [humanize, setHumanize] = useState(false);
    const [modelResponse, setModelResponse] = useState('');

    const handleSubmit = async () => {
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

            if (data.midiFile) {
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
                link.setAttribute('download', data.filename);
                link.click();
                window.URL.revokeObjectURL(url);
            }
        } else {
            const errorData = await response.json();
            setModelResponse("Fehler: " + errorData.error + "\nModellantwort: " + (errorData.modelResponse || "") + "\nDetails: " + (errorData.details || ""));
        }
    };

    return (
        <div className="container">
            <h1 className="title">CreativeChoon</h1>

            <label className="label" htmlFor="mood-textarea">
                Mood:
                <input
                    name="mood"
                    placeholder="Enter mood, favorite artist, etc."
                    className="input"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                />
            </label>

            <label className="label" htmlFor="bars-select">
                Bars:
                <select id="bars-select" name="bars" value={bars} onChange={(e) => setBars(e.target.value)} className="select">
                    <option value="4">4 bars</option>
                    <option value="8">8 bars</option>
                    <option value="16">16 bars</option>
                    <option value="32">32 bars</option>
                </select>
            </label>

            <label className="label" htmlFor="composition-select">
                Type:
                <select id="composition-select" name="compositionType" value={compositionType} onChange={(e) => setCompositionType(e.target.value)} className="select">
                    <option value="melody">melody</option>
                    <option value="chord">chord</option>
                </select>
            </label>

            <label className="label" htmlFor="bpm-input">
                BPM:
                <Input
                    id="bpm-input"
                    name="bpm"
                    type="number"
                    placeholder="Enter BPM"
                    value={bpm}
                    onChange={(e) => setBpm(e.target.value)}
                    className="input"
                />
            </label>

            <label className="label" htmlFor="oct-input">
                Oct:
                <Input
                    id="oct-input"
                    name="oct"
                    type="number"
                    placeholder="Enter Octave"
                    value={octave}
                    onChange={(e) => setOctave(e.target.value)}
                    className="input"
                />
            </label>

            <label className="label" htmlFor="humanize-input">
                Humanize:
                <input
                    id="humanize-input"
                    name="humanize"
                    type="checkbox"
                    checked={humanize}
                    onChange={(e) => setHumanize(e.target.checked)}
                    className="checkbox"
                />
            </label>

            <Button onClick={handleSubmit} className="button">
                <Send className="h-3 w-3 mr-2" /> Generate
            </Button>

            <div className="response-container">
                <h2>Model:</h2>
                <Textarea value={modelResponse} readOnly className="textarea" />
            </div>
        </div>
    );
}
