import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link} from 'react-router-dom';
import './Cities.css';

const Cities = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/cities');
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
        <div className="cities-container">
            <div className="cities-grid">
                {/* Map over the list of cities and render a card for each */}
                {data.cities.map(city => (
                    <div key={city.id} className="city-card">
                        <img src={city.image_url} alt="City" className="city-image" />
                        <div className="city-details">
                            <h3 className="city-name">{city.name}</h3>
                            <button className="follow-button">Follow</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Cities;
