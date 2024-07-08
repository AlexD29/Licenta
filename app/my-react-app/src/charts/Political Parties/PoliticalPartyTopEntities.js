import React, { useState, useEffect } from 'react';
import EmotionPieChart from 'charts/ArticleDetails/EmotionPieChart'; // Ensure this path is correct for your project

const PoliticalPartyTopEntities = ({ politicalPartyId }) => {
    const [topEntities, setTopEntities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [entityName, setEntityName] = useState([]);

    useEffect(() => {
        const fetchTopEntities = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/political-party-top-entities?political_party_id=${politicalPartyId}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok.');
                }
                const data = await response.json();
                setTopEntities(data.top_entities);
                setEntityName(data.political_party_name);
                setLoading(false);
            } catch (error) {
                setError('Error fetching data');
                setLoading(false);
            }
        };

        fetchTopEntities();
    }, [politicalPartyId]);

    if (loading) {
        return <p>Loading...</p>;
    }

    if (error) {
        return <p>{error}</p>;
    }

    return (
        <div className='articles-count-container'>
            <h2 className='title-h2'>Top Entități Asociate cu {entityName}</h2>
            <div>
                {topEntities.map(entity => (
                    <div className='top-3-row' key={entity.entity_id}>
                        <img src={entity.entity_image_url} alt={entity.entity_name} className='entity-image-box'/>
                        <span><strong>{entity.entity_name}</strong></span>
                        <EmotionPieChart
                            positive={entity.positive_count}
                            negative={entity.negative_count}
                            neutral={entity.neutral_count}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PoliticalPartyTopEntities;
