import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import "./Entities.css";
import { formatDate } from "../Articles";
import Footer from '../Footer';
import SourcesOverallEmotionDistribution from "charts/SourcesOverallEmotionDistribution";

const Entities = ({ userId, entityType, apiUrl, isSource }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [favorites, setFavorites] = useState(new Set());
  const [hiddenEntities, setHiddenEntities] = useState(new Set());
  const navigate = useNavigate();

  const fetchFavorites = async () => {
    try {
      const response = await axios.get("http://localhost:8000/api/favorites", {
        params: { user_id: userId },
      });
      setFavorites(
        new Set(
          response.data.map((item) => `${item.entity_id}-${item.entity_type}`)
        )
      );
    } catch (error) {
      console.error("Error fetching favorites:", error);
    }
  };

  const fetchHiddenEntities = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/api/hidden_entities",
        {
          params: { user_id: userId },
        }
      );
      setHiddenEntities(
        new Set(
          response.data.map((item) => `${item.entity_id}-${item.entity_type}`)
        )
      );
    } catch (error) {
      console.error("Error fetching hidden entities:", error);
    }
  };

  const handleFavoriteClick = async (entityId, entityType) => {
    try {
      const action = favorites.has(`${entityId}-${entityType}`)
        ? "remove"
        : "add";
      await axios.post("http://localhost:8000/api/favorites", {
        user_id: userId,
        entity_id: entityId,
        entity_type: entityType,
        action: action,
      });
      fetchFavorites();
    } catch (error) {
      console.error("Error updating favorites:", error);
    }
  };

  const handleHideClick = async (entityId, entityType) => {
    try {
      const action = hiddenEntities.has(`${entityId}-${entityType}`)
        ? "unhide"
        : "hide";
      await axios.post("http://localhost:8000/api/hidden_entities", {
        user_id: userId,
        entity_id: entityId,
        entity_type: entityType,
        action: action,
      });
      fetchHiddenEntities();
    } catch (error) {
      console.error("Error updating hidden entities:", error);
    }
  };

  const handleProfileClick = (entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (userId) {
          await fetchFavorites();
          await fetchHiddenEntities();
        }
        const response = await axios.get(apiUrl);
        setData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [apiUrl, userId]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!data) {
    return <div>Cannot explore now.</div>;
  }

  return (
    <div>
      <div className="entities-container">
        <div className="first-part">
          <SourcesOverallEmotionDistribution />
        </div>
        <div className="second-part">
          {data.map((entity) => {
            const entityKey = `${entity.id}-${entityType}`;
            if (hiddenEntities.has(entityKey)) return null;

            return (
              <div key={entityKey} className="entity-card">
                <div className={`entity-details ${entityType}-details`}>
                  <div className="entity-details-first-part">
                    <img
                      src={entity.image_url}
                      alt={entity.name || entity.title}
                      className="entity-image"
                    />
                    <h3 className="entity-name">
                      {entity.name ||
                        entity.abbreviation ||
                        `${entity.first_name} ${entity.last_name}`}
                    </h3>
                    <div className="button-container">
                      {!isSource && userId && (
                        <button
                          className={`profile-button follow-button ${
                            favorites.has(entityKey) ? "unfollow-button" : ""
                          }`}
                          onClick={() =>
                            handleFavoriteClick(entity.id, entityType)
                          }
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            width="24"
                            height="24"
                          >
                            <path
                              fill="currentColor"
                              d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
                            />
                          </svg>
                          <span className="tooltip-text">
                            {favorites.has(entityKey)
                              ? "Unfollow"
                              : "Add to favourites"}
                          </span>
                        </button>
                      )}
                      {!isSource && userId && (
                        <button
                          className="profile-button hide-button"
                          onClick={() => handleHideClick(entity.id, entityType)}
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
                      <button
                        className="profile-button profile-button-large"
                        onClick={() => handleProfileClick(entity.id)}
                      >
                        {isSource ? "Vezi Articolele" : "Vezi Profilul"}
                      </button>
                    </div>
                  </div>
                  <div className="entity-details-second-part"></div>
                </div>
                <div className="articles-container">
                  {entity.articles &&
                    entity.articles.map((article, index) => (
                      <Link
                        key={`${entity.id}-${article.id}`}
                        to={`/article/${article.id}`}
                        className="article-link-entity"
                      >
                        <div
                          className={`article-card-entity ${article.emotion.toLowerCase()} ${
                            index === entity.articles.length - 1
                              ? "last-article"
                              : ""
                          }`}
                        >
                          <div className="article-image-div-entity">
                            <img
                              src={article.image_url}
                              className="article-image-entity"
                            />
                          </div>
                          <div className="article-details-div-entity">
                            <h3 className="article-text-entity">
                              {article.title} -{" "}
                              <span className="published-date-entity-span">
                                {formatDate(article.published_date)}
                              </span>
                            </h3>
                          </div>
                        </div>
                      </Link>
                    ))}
                </div>
              </div>
            );
          })}
        </div>
        <div className="third-part">
          {/* <RomaniaMap /> */}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Entities;
