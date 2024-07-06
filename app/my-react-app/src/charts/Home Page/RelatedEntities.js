import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const RelatedEntities = ({ startDate, endDate }) => {
  const [relatedEntities, setRelatedEntities] = useState({
    most_positive: null,
    most_negative: null,
    most_neutral: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchRelatedEntities = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/related-entities",
          {
            params: {
              start_date: startDate,
              end_date: endDate,
            },
          }
        );

        console.log("API Response:", response.data);

        setRelatedEntities(response.data);
      } catch (error) {
        console.error("Error fetching related entities:", error);
        setError("Failed to fetch related entities.");
      } finally {
        setLoading(false);
      }
    };

    fetchRelatedEntities();
  }, [startDate, endDate]);

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  const renderEntity = (entity, sentimentType) => {
    if (!entity) return <div>No data available</div>;

    let percentage;
    if (sentimentType === "Positive") {
      percentage = entity.positive_percentage;
    } else if (sentimentType === "Negative") {
      percentage = entity.negative_percentage;
    } else {
      percentage = entity.neutral_percentage;
    }

    let categoryText;
    if (sentimentType === "Positive") {
      categoryText = "- pozitivitate -";
    } else if (sentimentType === "Negative") {
      categoryText = "- negativitate -";
    } else {
      categoryText = "- neutralitate -";
    }

    let percentageColor = "";
    let svgFillColor = "";
    if (sentimentType === "Positive") {
      percentageColor = "green";
      svgFillColor = "green"; // Green color for positive sentiment
    } else if (sentimentType === "Negative") {
      percentageColor = "red";
      svgFillColor = "red"; // Red color for negative sentiment
    } else {
      percentageColor = "gray";
      svgFillColor = "gray"; // Gray color for neutral sentiment
    }

    return (
      <div key={entity.entity_id} className="most-entity-item" onClick={() => handleProfileClick(entity.entity_type, entity.entity_id)}>
        <img
          src={entity.image_url}
          alt={entity.entity_name}
          className="most-image"
        />
        <div>
          <h3 className="most-name">{entity.entity_name}</h3>
          <p className="most-name-category" style={{ color: percentageColor }}>{categoryText}</p>
        </div>
        <div className="percentage-div">
          <p className="most-percentage-text" style={{ color: percentageColor }}>{percentage.toFixed(2)}%</p>
          <div>
            <svg
              className="percentage-svg"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill={svgFillColor} // Dynamically set fill color based on sentiment
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
    );
  };

  return (
    <div className="most-container">
      <h2 className="most-chart-title">Cele mai mari procentaje în ultima săptămână</h2>
      <div>{renderEntity(relatedEntities.most_positive, "Positive")}</div>
      <div>{renderEntity(relatedEntities.most_negative, "Negative")}</div>
      <div>{renderEntity(relatedEntities.most_neutral, "Neutral")}</div>
    </div>
  );
};

export default RelatedEntities;
