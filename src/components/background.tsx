import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react'; // Icons importieren
import './background.css';  // Import der CSS-Datei

const Background = () => {
    return (
        <div className="figma-creator-micro-top-view">
            <div className="base">
                <div className="translucent-borders"/>
                <div className="inside-edge-split"/>
                <div className="sascha-riemenschneider">by Sascha Riemenschneider</div>
                <div className="tobisstudio-2024">CreativeChoon © 2024 TobisStudio</div>
                <img className="smiley-icon" alt="Smiley" src="/background/smiley.svg"/>
                <div className="button-container">
                    <button className="open-button">
                        <ChevronLeft className="icon"/>
                        <span>Open</span>
                        <ChevronRight className="icon"/>
                    </button>
                </div>
                <div className="leds">
                    <div className="leds-child"/>
                    <div className="leds-item"/>
                    <div className="leds-inner"/>
                </div>
                {/* Container für die Würfel */}
                <div className="cube-container">
                    <img className="blue-cube" alt="Blue Cube" src="/mainimgs/blue.svg"/>
                    <img className="green-cube" alt="Green Cube" src="/mainimgs/green.svg"/>
                </div>
            </div>
        </div>
    );
};

export default Background;
