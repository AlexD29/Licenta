import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../Charts.css";

const TopEntityPairs = () => {
  const [topEntityPairs, setTopEntityPairs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTopEntityPairs = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/top-entity-pairs");
        const data = response.data.top_entity_pairs;
        setTopEntityPairs(data);
      } catch (error) {
        console.error("Error fetching top entity pairs:", error);
      }
    };

    fetchTopEntityPairs();
  }, []);

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  return (
    <div className="top-entity-pairs">
      <div className="title-div-box">
        <h3 className="box-title">
          Cel mai des menționate împreună săptămâna asta
        </h3>
      </div>
      {topEntityPairs.map((pair, index) => (
        <div key={index} className="entity-pair">
          <div className="entity1" onClick={() => handleProfileClick(pair.entity_type1, pair.entity_id1)}>
            <img
              src={pair.entity1_image_url}
              alt={pair.entity_name1}
              className={`entity-image-box ${pair.entity_type1}`}
            />
            <p className="entity-text">{pair.entity_name1}</p>
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
          <div className="entity2" onClick={() => handleProfileClick(pair.entity_type1, pair.entity_id2)}>
            <img
              src={pair.entity2_image_url}
              alt={pair.entity_name2}
              className={`entity-image-box ${pair.entity_type1}`}
            />
            <p className="entity-text">{pair.entity_name2}</p>
          </div>
          <div className="stats">
              <span className="total-text">{pair.pair_count}</span>
              <span className="positive">{pair.positive_count}</span>
              <span className="negative">{pair.negative_count}</span>
              <span className="neutral">{pair.neutral_count}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopEntityPairs;
