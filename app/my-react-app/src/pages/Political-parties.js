import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link} from 'react-router-dom';
import './Political_parties.css';

const Political_parties = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/explore');
                setData(response.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) {
        return (
          <div className="loading-container">
            <div className="loading-animation"></div>
            <p>Loading...</p>
          </div>
        );
      }

    if (!data) {
        return <div>Cannot explore now.</div>;
    }

    return (
        <div className="political-parties-container">
            <div className="political-parties-grid">
                {/* Map over the list of political parties and render a card for each */}
                {data.political_parties.map(party => (
                    <div key={party.id} className="party-card">
                        <img src={party.image_url} alt="Party" className="party-image" />
                        <div className="party-details">
                            <h3 className="party-abbreviation">{party.abbreviation}</h3>
                            <button className="follow-button">Follow</button>
                        </div>
                        
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Political_parties;
