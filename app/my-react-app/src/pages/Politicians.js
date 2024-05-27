import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './Politicians.css';

const Politicians = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/politician_articles');
                setData(response.data);
                console.log(response.data)
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
                <div className='first-section'></div>
                <div className='politicians-section'>
                {data.map(politician => (
                    <div key={politician.politician_id} className="politician-card">
                        <div className='politician-details'>
                            <div className="politician-details-first-part">
                                <img src={politician.image_url} alt="Politician" className="politician-image" />
                                <h3 className="politician-name">{politician.first_name} {politician.last_name}</h3>
                                <button className='follow-button'>Follow</button>
                            </div>
                            <div className='politician-details-second-part'>
                                <img className='profile-statistic-image' src='https://wac-cdn.atlassian.com/dam/jcr:978f9f05-19ee-47d5-a9a9-a768a601a61b/pie-chart-example-1.png?cdnVersion=1714'></img>
                            </div>
                        </div>
                        <div className="articles-container">
                            {politician.articles.slice(0,5).map(article => (
                                <div key={article.id} className="article-card">
                                    <img src={article.image_url} alt="Article" className="article-image" />
                                    <div className="article-details">
                                        {/* <h5 className="article-title">{article.title}</h5>
                                        <p className="article-author">{article.author}</p>
                                        <p className="article-published-date">{article.published_date}</p>
                                        <Link to={article.url} className="article-link">Read more</Link> */}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
                </div>
            <div className='statistics-section'>
                <img src='https://cdn1.byjus.com/wp-content/uploads/2021/03/bar-graph.png'></img>
                <img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQ4vgFKrbHkMQnKDyVGbsqsgvLyRZnAIzzIeSZ5pKxZQ&s'></img>
            </div>
        </div>
    );
};

export default Politicians;
