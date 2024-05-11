import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link} from 'react-router-dom';
import './Politicians.css';

const Politicians = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/politicians');
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
        <div className="politicians-container">
            <div className="politicians-grid">
                {data.politicians.map(politician => (
                    <div key={politician.id} className="politician-card">
                        <img src={politician.image_url} alt="Politician" className="politician-image" />
                        <div className="politician-details">
                            <h3 className="politician-name">{politician.first_name} {politician.last_name}</h3>
                            <p className="politician-position">{politician.position}</p>
                            <button className="follow-button">Follow</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Politicians;
