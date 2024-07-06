import React, { useState, useEffect } from 'react';
import axios from 'axios';
import "./Charts.css";

const RandomFactComponent = () => {
    const [randomFact, setRandomFact] = useState('');
    const [bgColor, setBgColor] = useState('');

    useEffect(() => {
        const fetchRandomFact = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/random-fact');
                setRandomFact(response.data.fact);
            } catch (error) {
                console.error('Error fetching random fact:', error);
            }
        };

        fetchRandomFact();
        randomizeBackgroundColor();
    }, []);

    const randomizeBackgroundColor = () => {
        const colors = ['#FF5722', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        setBgColor(randomColor);
    };

    return (
        <div className="fact-container" style={{ backgroundColor: bgColor }}>
            <h2 className='fact-title'>Știai că...?</h2>
            <div className="fact-box">
                <p className='fact-content'>{randomFact}</p>
            </div>
        </div>
    );
};

export default RandomFactComponent;
