import React, { useState, useEffect } from "react";
import "../Charts.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const TopEntitySuggestions = ({ userId, favorites, entityType, entities }) => {
  const navigate = useNavigate();
  const [favoriteEntities, setFavoriteEntities] = useState(new Set());
  const [hiddenEntities, setHiddenEntities] = useState(new Set());

  useEffect(() => {
    // Initialize favorite entities from the provided favorites prop
    const initialFavorites = new Set(
      favorites.map((fav) => `${fav[0]}-${fav[1]}`)
    );
    setFavoriteEntities(initialFavorites);
  }, [favorites]);

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  const handleFavoriteClick = async (entityId, entityType) => {
    const key = `${entityId}-${entityType}`;
    const isFavorited = favoriteEntities.has(key);

    try {
      const action = isFavorited ? "remove" : "add";
      await axios.post("http://localhost:8000/api/favorites", {
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
      console.error("Error updating favorites:", error);
    }
  };

  const handleHideClick = async (entityId, entityType) => {
    const key = `${entityId}-${entityType}`;
    const isHidden = hiddenEntities.has(key);

    try {
      const action = isHidden ? "unhide" : "hide";
      await axios.post("http://localhost:8000/api/hidden_entities", {
        user_id: userId,
        entity_id: entityId,
        entity_type: entityType,
        action: action,
      });

      setHiddenEntities(prev => {
        const updated = new Set(prev);
        if (isHidden) {
          updated.delete(key);
        } else {
          updated.add(key);
        }
        return updated;
      });
    } catch (error) {
      console.error("Error updating hidden entities:", error);
    }
  };

  return (
    <div className="top-entity-suggestions">
      <div className="box-title-div">
        <h2 className="entity-type-heading">Te-ar putea interesa...</h2>
      </div>
      <div className="entity-list">
        {entities.map((entity, index) => {
          const key = `${entity.entity_id}-${entityType}`;
          if (hiddenEntities.has(key)) {
            return null; // Don't render hidden entities
          }

          return (
            <div
              key={index}
              className="entity-item"
              onClick={() => handleProfileClick(entityType, entity.entity_id)}
            >
              <div className="img-div-suggestions">
                <img
                  src={entity.image_url}
                  alt={entity.entity_name}
                  className="entity-image-suggestions"
                />
              </div>
              <div className="entity-info">
                <h3 className="entity-name">{entity.entity_name}</h3>
              </div>
              <div className="button-container">
                {userId && (
                  <button
                    className={`profile-button follow-button ${
                      favoriteEntities.has(key) ? "favorited" : ""
                    }`}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleFavoriteClick(entity.entity_id, entityType);
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      width="24"
                      height="24"
                    >
                      <path
                        fill="currentColor"
                        d={
                          favoriteEntities.has(key)
                            ? "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                            : "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                        }
                      />
                    </svg>
                  </button>
                )}
                {userId && (
                  <button
                    className="profile-button hide-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleHideClick(entity.entity_id, entityType);
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      width="24"
                      height="24"
                    >
                      <path
                        fill="currentColor"
                        d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 13H7v-2h10v2z"
                      />
                    </svg>
                    <span className="tooltip-text"></span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TopEntitySuggestions;
