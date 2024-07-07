import React, { useState, useEffect } from 'react';
import EmotionPieChart from './EmotionPieChart';
import { useNavigate } from "react-router-dom";

const EntityPairComponent = ({ pairs }) => {
    const [pairResults, setPairResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    console.log(pairs);

    useEffect(() => {
        const fetchEntityPairAnalytics = async (entity1Id, entity1Type, entity2Id, entity2Type) => {
            setLoading(true);
            setError('');

            try {
                const response = await fetch(`http://localhost:8000/api/entity-pair-analytics?entity1Id=${entity1Id}&entity1Type=${entity1Type}&entity2Id=${entity2Id}&entity2Type=${entity2Type}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();
                return data;
            } catch (error) {
                setError('Failed to fetch data. Please try again later.');
                return null;
            } finally {
                setLoading(false);
            }
        };

        const fetchDataForPairs = async () => {
            const results = [];
            for (const pair of pairs) {
                const [entity1, entity2] = pair;
                const result = await fetchEntityPairAnalytics(entity1.entity_id, entity1.entity_type, entity2.entity_id, entity2.entity_type);
                if (result) {
                    results.push({
                        entity1_name: entity1.entity_name,
                        entity1_image_url: entity1.image_url,
                        entity2_name: entity2.entity_name,
                        entity2_image_url: entity2.image_url,
                        ...result,
                    });
                }
            }

            // Sort results by total articles in descending order
            results.sort((a, b) => b.counts.total - a.counts.total);

            // Take only the top 3 results
            const topResults = results.slice(0, 3);

            setPairResults(topResults);
        };

        if (pairs.length > 0) {
            fetchDataForPairs();
        }
    }, [pairs]);

    const handleProfileClick = (entityType, entityId) => {
        navigate(`/${entityType}/${entityId}`);
      };

    return (
        <div className="top-entity-pairs">
            <div className="title-div-box">
                <h3 className="box-title">
                    Întâlnite împreună în ultima săptămână
                </h3>
            </div>
            {loading && <p>Loading...</p>}
            {error && <p>{error}</p>}
            {pairResults.length > 0 ? (
                pairResults.map((result, index) => (
                    <div key={index} className="entity-pair">
                        <div className="entity1" onClick={() => handleProfileClick(result.entity1_type, result.entity1_id)}>
                            <img
                                src={result.entity1_image_url}
                                alt={result.entity1_name}
                                className={`entity-image-box ${result.entity1_type}`}
                            />
                            <p className="entity-text">{result.entity1_name}</p>
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
                        <div className="entity2" onClick={() => handleProfileClick(result.entity2_type, result.entity2_id)}>
                            <img
                                src={result.entity2_image_url}
                                alt={result.entity2_name}
                                className={`entity-image-box ${result.entity2_type}`}
                            />
                            <p className="entity-text">{result.entity2_name}</p>
                        </div>
                        <div className='stats'>
                        <EmotionPieChart
                            positive={result.counts.positive}
                            negative={result.counts.negative}
                            neutral={result.counts.neutral}
                        />
                        </div>
                    </div>
                ))
            ) : (
                <p>No data available</p>
            )}
        </div>
    );
};

export default EntityPairComponent;
