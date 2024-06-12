import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import Pagination from "./Pagination";
import { formatDate } from "../Articles";
import "./MyInterests.css";
import Footer from "../Footer";

const MyInterests = ({ userId }) => {
  const [favorites, setFavorites] = useState({});
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasFavorites, setHasFavorites] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    const fetchMyInterests = async (page = 1) => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/my_interests",
          {
            params: { user_id: userId, page },
          }
        );
        const favoriteEntities = response.data.favorite_entities || [];
        const groupedFavorites = favoriteEntities.reduce((acc, entity) => {
          const { type } = entity;
          if (!acc[type]) {
            acc[type] = [];
          }
          acc[type].push(entity);
          return acc;
        }, {});

        setFavorites(groupedFavorites);
        setArticles(response.data.related_articles || []);
        setTotalPages(response.data.total_pages || 1);
      } catch (error) {
        console.error("Error fetching my interests:", error);
        setError("Failed to load your interests. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchMyInterests(currentPage);
  }, [userId, currentPage]);

  useEffect(() => {
    setHasFavorites(
      Object.keys(favorites).some((type) => favorites[type].length > 0)
    );
  }, [favorites]);

  useEffect(() => {
    if (!hasFavorites) {
      // Fetch random suggestions
      fetch("http://localhost:8000/api/random-suggestions")
        .then((response) => response.json())
        .then((data) => {
          // Initialize suggestion favorite status
          const suggestionsWithFavoriteStatus = data.map(suggestion => ({
            ...suggestion,
            isFavorite: false,
          }));
          setSuggestions(suggestionsWithFavoriteStatus);
        })
        .catch((error) => console.error("Error fetching suggestions:", error));
    }
  }, [hasFavorites]);
  

  const handleRemove = async (id, type) => {
    const confirmRemove = window.confirm(
      "Are you sure you want to remove this favorite?"
    );
    if (confirmRemove) {
      try {
        const response = await axios.post(
          "http://localhost:8000/api/favorites",
          {
            user_id: userId,
            entity_id: id,
            entity_type: type,
            action: "remove",
          }
        );
        if (response.data.success) {
          setFavorites((prevFavorites) => {
            const updatedFavorites = { ...prevFavorites };
            updatedFavorites[type] = updatedFavorites[type].filter(
              (fav) => fav.id !== id
            );
            return updatedFavorites;
          });
        } else {
          console.error("Failed to remove favorite:", response.data.error);
        }
      } catch (error) {
        console.error("Error removing favorite:", error);
      }
    }
  };

  const handleAddFavorite = async (suggestion) => {
    try {
      const action = suggestion.isFavorite ? "remove" : "add";
  
      await axios.post("http://localhost:8000/api/favorites", {
        user_id: userId,
        entity_id: suggestion.id,
        entity_type: suggestion.type,
        action: action,
      });
  
      // Toggle the local favorite status of the suggestion
      setSuggestions((prevSuggestions) =>
        prevSuggestions.map((s) =>
          s.id === suggestion.id && s.type === suggestion.type
            ? { ...s, isFavorite: !s.isFavorite }
            : s
        )
      );
    } catch (error) {
      console.error("Error updating favorites:", error);
    }
  };
  

  const typeTranslations = {
    politician: "Politicieni",
    city: "Orașe",
    political_party: "Partide Politice",
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="interests-container">
      <div className="interests-content">
        <div
          className={`first-part ${
            hasFavorites ? "has-favorites" : "no-favorites"
          }`}
        >
          <div>
            <h2>Favorite</h2>
          </div>
          <div>
            {hasFavorites ? (
              <ul className="interests-list">
                {Object.keys(favorites).map(
                  (type) =>
                    favorites[type].length > 0 && (
                      <div key={type} className="favorite-category">
                        <h3>{typeTranslations[type]}</h3>
                        <ul>
                          {favorites[type].map((favorite) => (
                            <li
                              key={`${favorite.id}-${favorite.type}`}
                              className="favorite-entity"
                            >
                              <img
                                src={favorite.image_url}
                                className="alegeri-list-image"
                                alt={favorite.name}
                              />
                              {favorite.name}
                              <button
                                className="remove-button"
                                onClick={() =>
                                  handleRemove(favorite.id, favorite.type)
                                }
                              >
                                <svg
                                  id="Layer_1"
                                  data-name="Layer 1"
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 128 128"
                                  className="remove-svg"
                                >
                                  <defs></defs>
                                  <title>x</title>
                                  <path
                                    className="cls-1"
                                    d="M17.66229,21.88486,63.3847,30.82574l45.72241,8.94088a1.559,1.559,0,0,0,1.82788-1.22994A10.15176,10.15176,0,0,0,102.9192,26.6239l-15.172-2.96684.79656-4.07352A11.10952,11.10952,0,0,0,79.7827,6.56318L57.33412,2.17343A11.1096,11.1096,0,0,0,44.31375,10.9345L43.51718,15.008l-15.172-2.96685A10.15176,10.15176,0,0,0,16.43235,20.057a1.559,1.559,0,0,0,1.22994,1.82788ZM60.0674,9.82374,74.369,12.62036a8.2641,8.2641,0,0,1,6.5245,9.69647h0l-15.2613-2.9843L50.37093,16.34825h0A8.2641,8.2641,0,0,1,60.0674,9.82374Z"
                                  ></path>
                                  <path
                                    className="cls-2"
                                    d="M110.58839,47.36161H17.41161a1.559,1.559,0,0,0-1.55785,1.55785v5.90918c0,.85949,16.14275,61.05238,16.14275,61.05238a11.08149,11.08149,0,0,0,11.03938,10.153H84.96412A11.08149,11.08149,0,0,0,96.0035,115.881s16.14275-60.19289,16.14275-61.05238V48.91946A1.559,1.559,0,0,0,110.58839,47.36161Zm-61.934,64.2194a2.60793,2.60793,0,0,1-3.19666-1.84821c-4.44239-16.61345-8.95983-33.53068-11.91535-44.72956a2.61069,2.61069,0,1,1,5.04851-1.33243c2.95407,11.19159,7.47077,28.10409,11.911,44.71353A2.61043,2.61043,0,0,1,48.65435,111.581Zm17.95316-2.52243a2.61095,2.61095,0,0,1-5.22189,0V64.337a2.61095,2.61095,0,0,1,5.22189,0ZM94.45735,65.00325C91.3685,76.70879,86.46715,95.05644,82.542,109.73317a2.61073,2.61073,0,1,1-5.04414-1.34918c3.9237-14.67272,8.8236-33.01491,11.911-44.71316a2.61069,2.61069,0,1,1,5.04851,1.33243Z"
                                  ></path>
                                </svg>
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )
                )}
              </ul>
            ) : (
              <div className="no-favorites">
                <p className="suggestions-text-favorite">
                  Nu ai încă favorite. Iată câteva sugestii pentru tine:
                </p>
                <ul className="suggestions-list-favorites">
                  {suggestions.map((suggestion) => {
                    return (
                      <li
                        key={`${suggestion.id}-${suggestion.type}`}
                        className="suggestions-entity-favorites"
                      >
                        <Link to={`/${suggestion.type}/${suggestion.id}`} className="suggestion-link-favorites">
                          <img
                            src={suggestion.image_url}
                            className="suggestions-list-image-favorite"
                            alt={suggestion.name}
                          />
                          <span>{suggestion.name}</span>
                        </Link>
                        <button
                          className={`follow-button-suggestions-favorite ${
                            suggestion.isFavorite ? "remove" : "add"
                          }`}
                          onClick={() => handleAddFavorite(suggestion)}
                        >
                          {suggestion.isFavorite
                            ? "Elimina de la favorite"
                            : "Adaugă la favorite"}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            )}
          </div>
        </div>
        {hasFavorites && (
          <div className="second-part">
            <div className="articles-part">
              {articles.map((article) => (
                <Link
                  key={article.id}
                  to={`/article/${article.id}`}
                  className="article-link-minimized"
                >
                  <div
                    className={`article-card-minimized ${article.emotion.toLowerCase()}`}
                  >
                    <div className="article-image-div-minimized">
                      <img
                        src={article.image_url}
                        className="article-image-minimized"
                        alt="Article"
                      />
                    </div>
                    <div className="article-details-div-minimized">
                      <h3 className="article-text-minimized">
                        {article.title}
                      </h3>
                      <p className="article-text-minimized">
                        {formatDate(article.published_date)}
                      </p>
                    </div>
                    <div className="article-source-image-minimized">
                      <img
                        src={article.source_image_url}
                        alt={article.source_name}
                        className="source-icon-minimized"
                      />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </div>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default MyInterests;
