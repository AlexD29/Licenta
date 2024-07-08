import React, { useEffect, useState } from 'react';
import axios from 'axios';

const EntityRankComponent = ({ entityType, entityId }) => {
  const [entityData, setEntityData] = useState([]);

  useEffect(() => {
    const fetchEntityData = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/entity-rank?entity_type=${entityType}&entity_id=${entityId}`);
        setEntityData(response.data);
      } catch (error) {
        console.error('Error fetching entity data:', error);
      }
    };

    fetchEntityData();
  }, [entityType, entityId]);

  console.log(entityData);

  return (
    <div className='articles-count-container'>
      <h2 className='title-h2'># După numărul de articole</h2>
      <div className="entity-grid">
        {entityData.slice(0,3).map(entity => (
          <div className='top-3-row-rank' key={entity.entity_id}>
            <span><strong>{entity.rank}.</strong></span>
            <img src={entity.image_url} alt={entity.entity_name} className='entity-image-box'/>
            <span><strong>{entity.name}</strong></span>
            <span>{entity.total_articles} articole</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EntityRankComponent;
