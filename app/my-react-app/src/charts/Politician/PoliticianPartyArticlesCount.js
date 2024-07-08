import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const PoliticianPartyArticlesCount = ({ politicianId, politicalPartyId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArticlesCount = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/politician-party-articles-count?politician_id=${politicianId}&political_party_id=${politicalPartyId}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const result = await response.json();
        setData(result);
        setLoading(false);
      } catch (error) {
        setError(error.message);
        setLoading(false);
      }
    };

    fetchArticlesCount();
  }, [politicianId, politicalPartyId]);

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  if (!data) {
    return <p>No data available</p>;
  }

  return (
    <div className="articles-count-container">
      <h2 className="h2-politician-political-party">
        Apariții împreună cu partidul
      </h2>
      <div className="entity-pair-2">
        <div
          className="entity-politician-party"
          onClick={() => handleProfileClick("politician", politicianId)}
        >
          <img
            src={data.politician_image_url}
            alt={data.politician_name}
            className={`entity-image-box`}
          />
          <p className="entity-text">{data.politician_name}</p>
        </div>
        <div className="plus-svg-div">
          <svg
            className="plus-svg"
            version="1.1"
            id="Capa_1"
            xmlns="http://www.w3.org/2000/svg"
            x="0px"
            y="0px"
            viewBox="0 0 402 402"
          >
            <style type="text/css"></style>
            <g>
              <linearGradient
                id="SVGID_1_"
                gradientUnits="userSpaceOnUse"
                x1="0"
                y1="200.997"
                x2="401.993"
                y2="200.997"
              >
                <stop offset="0"></stop>
                <stop offset="1"></stop>
              </linearGradient>
              <path
                className="st0"
                d="M394,154.2c-5.3-5.3-11.8-8-19.4-8H255.8V27.4c0-7.6-2.7-14.1-8-19.4c-5.3-5.3-11.8-8-19.4-8h-54.8
                c-7.6,0-14.1,2.7-19.4,8s-8,11.8-8,19.4v118.8H27.4c-7.6,0-14.1,2.7-19.4,8S0,166,0,173.6v54.8c0,7.6,2.7,14.1,8,19.4
                c5.3,5.3,11.8,8,19.4,8h118.8v118.8c0,7.6,2.7,14.1,8,19.4c5.3,5.3,11.8,8,19.4,8h54.8c7.6,0,14.1-2.7,19.4-8
                c5.3-5.3,8-11.8,8-19.4V255.8h118.8c7.6,0,14.1-2.7,19.4-8c5.3-5.3,8-11.8,8-19.4v-54.8C402,166,399.3,159.5,394,154.2z"
              ></path>
            </g>
          </svg>
        </div>
        <div
          className="entity-politician-party a-doua"
          onClick={() =>
            handleProfileClick("political-party", politicalPartyId)
          }
        >
          <img
            src={data.political_party_image_url}
            alt={data.political_party_name}
            className={`entity-image-box`}
          />
          <p className="entity-text">{data.political_party_name}</p>
        </div>
      </div>
      <div className="party-relation-stats">
        <div className="p-element-stats">
            <p className="up-p">
            {data.joint_articles}/{data.total_articles}
            </p>
            <p className="down-p">articole</p>
        </div>
        <div className="p-element-stats">
            <p className="up-p">{data.percentage.toFixed(2)}%</p>
            <div>
                <svg
                className="percentage-svg"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill={'black'} // Dynamically set fill color based on sentiment
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
    </div>
  );
};

export default PoliticianPartyArticlesCount;
