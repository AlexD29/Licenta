import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./SourceCharts.css"; // Import the CSS file

function keepIntegerPart(percentage) {
  return Math.floor(percentage);
}

function TopPositiveEntities({ sourceId }) {
  const [topEntities, setTopEntities] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/top-entities/${sourceId}`
        );
        console.log("Fetched data:", response.data);
        setTopEntities(response.data.top_entities.slice(0, 3)); // Limit to top 3 entities
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [sourceId]);

  const handleCardClick = (entity) => {
    navigate(`/${entity.entity_type}/${entity.entity_id}`);
  };

  return (
    <div className="top-entities-container">
      <h2 className="top-3-text">Top 3 Cele mai pozitive</h2>
      <div className="top-entities-cards">
        {topEntities.map((entity) => (
          <div
            key={entity.entity_id}
            onClick={() => handleCardClick(entity)}
            className="top-entity-card"
          >
            <img src={entity.image_url} alt={entity.entity_name} />
            <h3>{entity.entity_name}</h3>
            <div className="articles-number-div">
              <p className="number-of-articles-text positive-text">{keepIntegerPart(entity.positive_percentage)}%</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TopPositiveEntities;
