import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link} from 'react-router-dom';
import './Explore.css';

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
        <div className="explore-container">
            <div className="card">
            <Link to="/elections">
                <div className='title-div'>
                    <h2 className="card-title">2024 Elections</h2>
                </div>
                <div className="main-image">
                    <img src="./explore/alegeri-2024.jpg" alt="Election 2024" className="card-image" />
                </div>
                <ul>
                    <li className="elections-list-item">
                        <img src="./explore/alegeri-europarlamentare.jpg" alt="Image" className="list-image" />
                        <div>
                            <p>European Parliamentary Elections</p>
                            <p>June 9</p>
                        </div>
                    </li>
                    <li className="elections-list-item">
                        <img src="./explore/alegeri-locale.jpg" alt="Image" className="list-image" />
                        <div>
                            <p>Local Elections</p>
                            <p>June 9</p>
                        </div>
                    </li>
                    <li className="elections-list-item">
                        <img src="./explore/alegeri-prezidentiale.jpg" alt="Image" className="list-image" />
                        <div>
                            <p>Presidential Elections</p>
                            <p>September 15 and 29</p>
                        </div>
                    </li>
                    <li className="elections-list-item">
                        <img src="./explore/alegeri-parlamentare.jpg" alt="Image" className="list-image" />
                        <div>
                            <p>Parliamentary Elections</p>
                            <p>December 8</p>
                        </div>
                    </li>
                </ul>
            </Link>
        </div>

        <div className="card">
            <Link to="/politicians" className='link-card'>
                <div className='title-div'>
                    <h2 className="card-title">Politicians</h2>
                </div>
                <div className="main-image">
                    <img src="./explore/politicians-picture.jpg" alt="Election 2024" className="card-image" />
                </div>
                <div className="top-3-this-week-div">
                    <h3 className='top-3-this-week'>Top 3 This Week</h3>
                </div>
                <ul>
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
                    <p>+ more</p>
                </div>
            </Link>
        </div>


            <div className="card">
                <Link to="/political-parties" className='link-card'>
                    <div className='title-div'>
                        <h2 className="card-title">Political Parties</h2>
                    </div>
                    <div className="main-image">
                        <img src="./explore/political_parties-picture.jpg" alt="Election 2024" className="card-image" />
                    </div>
                    <div className="top-3-this-week-div">
                        <h3 className='top-3-this-week'>Top 3 This Week</h3>
                    </div>
                    <ul>
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
                        <p>+ more</p>
                    </div>
                </Link>
            </div>

            <div className="card">
                <Link to="/cities" className='link-card'>
                    <div className='title-div'>
                        <h2 className="card-title">Cities</h2>
                    </div>
                    <div className="main-image">
                        <img src="./explore/cities-picture.jpg" alt="Election 2024" className="card-image" />
                    </div>
                    <div className="top-3-this-week-div">
                        <h3 className='top-3-this-week'>Top 3 This Week</h3>
                    </div>
                    <ul>
                        {data.cities.slice(0,3).map(city => (
                            <li key={city.id} className="elections-list-item">
                                <img src={city.image_url} alt="Image" className="list-image"/>
                                <div>{city.name}</div>
                            </li>
                        ))}
                    </ul>
                    <div className="more-button">
                        <p>+ more</p>
                    </div>
                </Link>
            </div>

        </div>
    );
};

export default Explore;
