import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import Pagination from "./Pagination";
import { formatDate } from "../Articles";
import "./MyInterests.css";
import Footer from "../Footer";
import { useNavigate } from "react-router-dom";
import { truncateTitle } from "../Articles";
import CityTopEntities from "charts/City/CityTopEntities";
import PoliticianSourcesChart from "charts/Politician/PoliticianSourcesChart";
import NegativeSources from "charts/Politician/NegativeSources";
import PositiveSources from "charts/Politician/PositiveSources";
import EntityRankComponent from "charts/Politician/EntityRankComponent";
import CityArticlesDistribution from "charts/City/CityArticlesDistribution";
import CityArticlesChart from "charts/City/CityArticlesChart";
import TopCityAuthorsPieChart from "charts/City/TopCityAuthorsPieChart";
import TopPoliticalPartyAuthorsPieChart from "charts/Political Parties/TopPoliticalPartyAuthorsPieChart";
import PoliticalPartyArticlesDistribution from "charts/Political Parties/PoliticalPartyArticlesDistribution";
import PoliticalPartyArticlesChart from "charts/Political Parties/PoliticalPartyArticlesChart";
import PoliticalPartyTopEntities from "charts/Political Parties/PoliticalPartyTopEntities";
import PoliticianArticlesDistribution from "charts/Politician/PoliticianArticlesDistribution";
import PoliticianArticlesChart from "charts/Politician/PoliticianArticlesChart";
import PoliticianPartyArticlesCount from "charts/Politician/PoliticianPartyArticlesCount";
import PoliticianTopEntities from "charts/Politician/PoliticianTopEntities";
import TopPoliticianAuthorsPieChart from "charts/Politician/TopPoliticianAuthors";

const politicianCharts = (id, politician) => [
  <PoliticianArticlesDistribution politicianId={id} />,
  <PoliticianArticlesChart politicianId={id} />,
  <PoliticianSourcesChart entityId={id} entityType="politician" />,
  <NegativeSources entityId={id} entityType="politician" />,
  <PositiveSources entityId={id} entityType="politician" />,
  <PoliticianTopEntities politicianId={id} />,
  <TopPoliticianAuthorsPieChart politicianId={id} />,
  <EntityRankComponent entityId={id} entityType='politician' />,
];

const politicalPartyCharts = (id) => [
  <PoliticalPartyArticlesDistribution politicalPartyId={id} />,
  <PoliticalPartyArticlesChart politicalPartyId={id} />,
  <PoliticianSourcesChart entityId={id} entityType="political-party" />,
  <NegativeSources entityId={id} entityType="political-party" />,
  <PositiveSources entityId={id} entityType="political-party" />,
  <PoliticalPartyTopEntities politicalPartyId={id} />,
  <TopPoliticalPartyAuthorsPieChart politicalPartyId={id} />,
  <EntityRankComponent entityId={id} entityType='political_party' />,
];

const cityCharts = (id) => [
  <CityArticlesDistribution cityId={id} />,
  <CityArticlesChart cityId={id} />,
  <PoliticianSourcesChart entityId={id} entityType="city" />,
  <NegativeSources entityId={id} entityType="city" />,
  <PositiveSources entityId={id} entityType="city" />,
  <CityTopEntities cityId={id} />,
  <TopCityAuthorsPieChart cityId={id} />,
  <EntityRankComponent entityId={id} entityType='city' />,
];


const MyInterests = ({ userId }) => {
  const [favorites, setFavorites] = useState({});
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasFavorites, setHasFavorites] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [userChecked, setUserChecked] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const verifyUser = async () => {
      if (!userId) {
        setUserChecked(true);
        return;
      }

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
          setUserChecked(true); // Set to true after checking user ID
        }
      };

      fetchMyInterests(currentPage);
    };

    verifyUser();
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

  const collectAllCharts = (favorites) => {
    const allCharts = [];

    // Collect all charts from all favorite entities
    Object.keys(favorites).forEach(type => {
      favorites[type].forEach(entity => {
        switch (type) {
          case "politician":
            allCharts.push(...politicianCharts(entity.id, entity));
            break;
          case "political-party":
            allCharts.push(...politicalPartyCharts(entity.id));
            break;
          case "city":
            allCharts.push(...cityCharts(entity.id));
            break;
          default:
            break;
        }
      });
    });

    return allCharts;
  };

  const getRandomCharts = (charts) => {
    const shuffledCharts = charts.sort(() => Math.random() - 0.5);
    return shuffledCharts.slice(0, 6); // Limit to 6 charts
  };
  
  useEffect(() => {
    if (userChecked && !loading && !error && hasFavorites) {
      const allCharts = collectAllCharts(favorites);
      const randomCharts = getRandomCharts(allCharts);
      setDisplayedCharts(randomCharts);
    }
  }, [userChecked, loading, error, hasFavorites, favorites]);

  const [displayedCharts, setDisplayedCharts] = useState([]);

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
    'political-party': "Partide Politice",
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleProfileClick = (entityType, entityId) => {
    navigate(`/${entityType}/${entityId}`);
  };

  if (!userChecked) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className={`interests-container ${!userChecked ? "hidden-content" : ""}`}>
    {!userId ? (
    <div>
      <div className="not-logged-in">
        <div className="redirect-to-login-div big-div">
          <div className="small-div">
            <h1>Trebuie să fii autentificat pentru a-ți vedea interesele.</h1>
            <Link to="/login" className="login-link"><h2>Spre Login</h2></Link>
          </div>
          <hr className="custom-hr"/>
          <h1>De ce sa-ti faci cont?</h1>
          <p>
            Crearea unui cont pe platforma noastră vă oferă o experiență personalizată și adaptată preferințelor dumneavoastră. Prin autentificare, aveți acces la o serie de funcționalități exclusive care vă vor ajuta să rămâneți informat și să primiți doar știri care vă interesează cu adevărat.
          </p>
          <p>
            Una dintre principalele beneficii ale creării unui cont este posibilitatea de a adăuga entități la favorite. Astfel, veți primi cele mai recente și relevante știri despre politicienii, partidele politice sau orașele care vă interesează cel mai mult. Nu mai pierdeți timp căutând informațiile dorite, deoarece acestea vor fi aduse direct la dumneavoastră.
          </p>
          <p>
            De asemenea, puteți ascunde știrile pe care nu doriți să le vedeți. Prin filtrarea conținutului nedorit, veți avea o experiență de citire mult mai plăcută și eficientă. Puteți să vă concentrați doar pe ceea ce contează pentru dumneavoastră, fără a fi deranjați de subiecte irelevante.
          </p>
          <p>
            Un alt avantaj al contului este accesul la statistici și analize detaliate. Vă oferim informații despre tonul știrilor (pozitiv, negativ sau neutru) și cum sunt percepuți diferiți politicieni sau partide politice. Aceste statistici vă ajută să înțelegeți mai bine peisajul politic și să luați decizii informate.
          </p>
          <p>
            În concluzie, crearea unui cont pe platforma noastră nu doar că îmbunătățește experiența de utilizare, dar vă oferă și instrumentele necesare pentru a rămâne informat și a avea o perspectivă clară asupra știrilor politice. Nu ratați aceste beneficii - creați un cont și autentificați-vă pentru a profita la maximum de toate funcționalitățile disponibile.
          </p>
          <div className="my-interests-image" style={{ maskImage: `url(/icons/WDIVW_text_logo.png)`, WebkitMaskImage: `url(/icons/WDIVW_text_logo.png)` }} alt="Despre Noi"></div>
        </div>
      </div>
      <Footer />
    </div>
    ) : (
    <div className="interests-container">
      <div className="interests-content">
        <div
          className={`${
            hasFavorites ? "first-part-favorite" : "no-favorites-part"
          }`}
        >
          <div>
            <h2 className="favorites-text">Favorite</h2>
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
                              onClick={() => handleProfileClick(favorite.type, favorite.id)}
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
          <div className="favorites-columns">
            <div className="second-part-favorite">
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
                          alt=""
                        />
                      </div>
                      <div className="article-details-div-minimized">
                        <h3 className="article-text-minimized">
                          {truncateTitle(article.title, 130)}
                        </h3>
                        <div className="article-date-and-source">
                          <p className="article-text-minimized">
                            {formatDate(article.published_date)}
                          </p>
                          <div className="article-source-image-minimized">
                            <img
                              src={article.source_image_url}
                              alt={article.source_name}
                              className="source-icon-minimized"
                            />
                          </div>
                        </div>
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
            <div className="third-part-favorite">
              {displayedCharts.map((ChartComponent, index) => (
                <div key={index} className="chart-container">
                  {ChartComponent}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <Footer />
    </div>
    )}
    </div>
  );
};

export default MyInterests;
