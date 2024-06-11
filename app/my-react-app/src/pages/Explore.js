import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link} from 'react-router-dom';
import './Explore.css';
import Footer from '../Footer';

const Explore = () => {
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
        <div className='main-container'>
            <div className="explore-container">
                <div className="card">
                <Link to="/alegeri/toate-alegerile">
                    <div className='title-div'>
                        <h2 className="card-title">Alegeri 2024</h2>
                    </div>
                    <div className="main-image">
                        <img src="./explore/alegeri-2024.jpg" alt="Election 2024" className="card-image" />
                    </div>
                    <ul className='elections-list'>
                        <li className="elections-list-item">
                            <img src="./explore/alegeri-europarlamentare.jpg" alt="Image" className="list-image" />
                            <div className='elections-text-div'>
                                <p>Alegeri Europarlamentare</p>
                                <p>9 Iunie</p>
                            </div>
                        </li>
                        <li className="elections-list-item">
                            <img src="./explore/alegeri-locale.jpg" alt="Image" className="list-image" />
                            <div className='elections-text-div'>
                                <p>Alegeri Locale</p>
                                <p>9 Iunie</p>
                            </div>
                        </li>
                        <li className="elections-list-item">
                            <img src="./explore/alegeri-prezidențiale.jpg" alt="Image" className="list-image" />
                            <div className='elections-text-div'>
                                <p>Alegeri Prezidențiale</p>
                                <p>15 și 29 Septembrie</p>
                            </div>
                        </li>
                        <li className="elections-list-item">
                            <img src="./explore/alegeri-parlamentare.jpg" alt="Image" className="list-image" />
                            <div className='elections-text-div'>
                                <p>Alegeri Parlamentare</p>
                                <p>8 Decembrie</p>
                            </div>
                        </li>
                    </ul>
                </Link>
                </div>
                <div className="card">
                    <Link to="/politicians" className='link-card'>
                        <div className='title-div'>
                            <h2 className="card-title">Politicieni</h2>
                        </div>
                        <div className="main-image">
                            <img src="./explore/politicians-picture.jpg" alt="Election 2024" className="card-image" />
                        </div>
                        <div className="top-3-this-week-div">
                            <h3 className='top-3-this-week'>Top 3 Săptămâna asta</h3>
                        </div>
                        <ul className='explore-card-list'>
                            {data.politicians.slice(0, 3).map(politician => (
                                <li key={politician.id} className="elections-list-item">
                                    <img src={politician.image_url} alt="Image" className="list-image" />
                                    <div>
                                        {politician.first_name} {politician.last_name}
                                    </div>
                                </li>
                            ))}
                        </ul>
                        <div className="more-button">
                            <p>+ mai mulți</p>
                        </div>
                    </Link>
                </div>
                <div className="card">
                    <Link to="/political-parties" className='link-card'>
                        <div className='title-div'>
                            <h2 className="card-title">Partide Politice</h2>
                        </div>
                        <div className="main-image">
                            <img src="./explore/political_parties-picture.jpg" alt="Election 2024" className="card-image" />
                        </div>
                        <div className="top-3-this-week-div">
                            <h3 className='top-3-this-week'>Top 3 Săptămâna asta</h3>
                        </div>
                        <ul className='explore-card-list'>
                            {data.political_parties.slice(0,3).map(party => (
                                <li key={party.id} className="elections-list-item">
                                    <img src={party.image_url} alt="Image" className="list-image" />
                                    <div>
                                        {party.abbreviation}
                                    </div>
                                </li>
                            ))}
                        </ul>
                        <div className="more-button">
                            <p>+ mai multe</p>
                        </div>
                    </Link>
                </div>
                <div className="card">
                    <Link to="/cities" className='link-card'>
                        <div className='title-div'>
                            <h2 className="card-title">Orașe</h2>
                        </div>
                        <div className="main-image">
                            <img src="./explore/cities-picture.jpg" alt="Election 2024" className="card-image" />
                        </div>
                        <div className="top-3-this-week-div">
                            <h3 className='top-3-this-week'>Top 3 Săptămâna asta</h3>
                        </div>
                        <ul className='explore-card-list'>
                            {data.cities.slice(0,3).map(city => (
                                <li key={city.id} className="elections-list-item">
                                    <img src={city.image_url} alt="Image" className="list-image"/>
                                    <div>{city.name}</div>
                                </li>
                            ))}
                        </ul>
                        <div className="more-button">
                            <p>+ mai multe</p>
                        </div>
                    </Link>
                </div>
                <div className="card">
                    <Link to="/sources" className='link-card'>
                        <div className='title-div'>
                            <h2 className="card-title">Surse</h2>
                        </div>
                        <div className="main-image">
                            <img src="./explore/cities-picture.jpg" alt="Election 2024" className="card-image" />
                        </div>
                        <div className="top-3-this-week-div">
                            <h3 className='top-3-this-week'>Top 3 Săptămâna asta</h3>
                        </div>
                        <ul className='explore-card-list'>
                            {data.sources.map(source => (
                                <li key={source.id} className="elections-list-item">
                                    <img src={source.image_url} alt="Image" className="list-image"/>
                                    <div>{source.name}</div>
                                </li>
                            ))}
                        </ul>
                        <div className="more-button">
                            <p>+ mai multe</p>
                        </div>
                    </Link>
                </div>
            </div>
            <Footer />
        </div>
    );
};

export default Explore;
