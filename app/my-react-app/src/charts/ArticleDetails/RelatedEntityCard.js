import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../Charts.css';
import EntityChart from './EntityChart';
import { useNavigate } from 'react-router-dom';

function RelatedEntityCard({ userId, entityType, entityName, entityImage, entityId, favorites }) {
  const [entityData, setEntityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [favoriteEntities, setFavoriteEntities] = useState(new Set());
  const navigate = useNavigate();

    console.log(userId);

  useEffect(() => {
    const fetchEntityData = async () => {
      try {
        const endDate = new Date().toISOString().split('T')[0];
        const startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        const response = await axios.get(`http://localhost:8000/api/entity-articles`, {
          params: {
            entityId,
            entityType,
            start_date: startDate,
            end_date: endDate,
          },
        });
        setEntityData(response.data.counts);
      } catch (err) {
        setError('Error fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchEntityData();
  }, [entityId, entityType]);

  useEffect(() => {
    // Initialize favorite entities from the provided favorites prop
    const initialFavorites = new Set(favorites.map((fav) => `${fav[0]}-${fav[1]}`));
    setFavoriteEntities(initialFavorites);
  }, [favorites]);

  const handleFavoriteClick = async (e, entityId, entityType) => {
    e.stopPropagation(); // Prevent triggering the profile click event
    const key = `${entityId}-${entityType}`;
    const isFavorited = favoriteEntities.has(key);

    try {
      const action = isFavorited ? 'remove' : 'add';
      await axios.post('http://localhost:8000/api/favorites', {
        user_id: userId,
        entity_id: entityId,
        entity_type: entityType,
        action: action,
      });

      setFavoriteEntities((prev) => {
        const updated = new Set(prev);
        if (isFavorited) {
          updated.delete(key);
        } else {
          updated.add(key);
        }
        return updated;
      });
    } catch (error) {
      console.error('Error updating favorites:', error);
    }
  };

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  const isFavorited = favoriteEntities.has(`${entityId}-${entityType}`);

  return (
    <div className="related-entity-card" onClick={() => handleProfileClick(entityType, entityId)}>
      <div className="related-entity-info">
        <img src={entityImage} alt={entityName} className="related-entity-image" />
        <div>
          <h3>{entityName}</h3>
          <div className="profile-button-div-political-party">
            <button
              className={`follow-button-profile ${!userId ? 'inactive' : isFavorited ? 'remove' : 'add'}`}
              onClick={(e) => handleFavoriteClick(e, entityId, entityType)}
              disabled={!userId}
            >
              {isFavorited ? 'Nu mai urmări' : 'Urmarește'}
            </button>
          </div>
        </div>
      </div>
      <div className="entity-mini-chart">
        <EntityChart
          entityName={entityName}
          positive={entityData.positive}
          negative={entityData.negative}
          neutral={entityData.neutral}
        />
      </div>
    </div>
  );
}

export default RelatedEntityCard;
