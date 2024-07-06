import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RelatedEntities = ({ articleId }) => {
  const [relatedEntities, setRelatedEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRelatedEntities = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/related-entities/${articleId}`);
        setRelatedEntities(response.data.related_entities);
        setLoading(false);
      } catch (err) {
        setError(err);
        setLoading(false);
      }
    };

    fetchRelatedEntities();
  }, [articleId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error loading related entities: {error.message}</div>;

  return (
    <div>
      <h2>Related Entities</h2>
      {relatedEntities.length === 0 ? (
        <p>No related entities found.</p>
      ) : (
        <div>
          {relatedEntities.map((entity) => (
            <div key={entity.entity_id} className="entity">
              <img src={entity.image_url} alt={entity.entity_name} width={50} height={50} />
              <div>
                <h3>{entity.entity_name}</h3>
                <p>Type: {entity.entity_type}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RelatedEntities;
