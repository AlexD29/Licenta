import React, { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";

const PositiveSources = ({ entityId, entityType }) => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [entityName, setEntityName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPositiveSources = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/entity-sources-most-positive/${entityId}?entity_type=${entityType}`);
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const data = await response.json();
        setSources(data.sources);
        setEntityName(data.entity_name);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };

    fetchPositiveSources();
  }, [entityId, entityType]);

  const handleCardClick = (source) => {
    navigate(`/source/${source.id}`);
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div className="top-entities-container positive-chart">
      <h2 className="top-3-text">Sursele cu cea mai mare pozitivitate<br/>față de {entityName}</h2>
      {sources.length === 0 ? (
        <p>No data available</p>
      ) : (
        <div className="top-entities-cards">
            {sources.map((source) => (
            <div
                key={source.entity_id}
                onClick={() => handleCardClick(source)}
                className="top-entity-card"
            >
                <img className='top-img' src={source.image_url} alt={source.source_name} />
                <h3>{source.name}</h3>
                <div className="articles-number-div">
                    <p className="number-of-articles-text positive-text">{Math.floor(source.positive_percentage)}%</p>
                    <div>
                        <svg
                        className="percentage-svg"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill={'green'} // Dynamically set fill color based on sentiment
                        >
                        <g>
                            <path fill="none" d="M0 0h24v24H0z"></path>
                            <path
                            d="M11 2.05V13h10.95c-.501 5.053-4.765 9-9.95 9-5.523 0-10-4.477-10-10 0-5.185 3.947-9.449 9-9.95zm2 0A10.003 10.003 0 0 1 21.95 11H13V2.05z"
                            ></path>
                        </g>
                        </svg>
                    </div>
                </div>
            </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default PositiveSources;
