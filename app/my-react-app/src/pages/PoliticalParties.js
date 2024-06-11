import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./PoliticalParties.css";
import { formatDate } from "../Articles";

const PoliticalParties = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);

  const handleFollowClick = (partyId) => {
    setIsFollowing((prevState) => ({
      ...prevState,
      [partyId]: !prevState[partyId],
    }));
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          "http://localhost:8000/api/political_parties_articles"
        );
        setData(response.data);
        console.log(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

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
    <div className="entity-container">
      <div className="first-section"></div>
      <div className="entity-section">
        {data.map((party) => (
          <div key={party.party_id} className="entity-card">
            <div className="entity-details party-details">
              <div className="entity-details-first-part">
                <img
                  src={party.image_url}
                  alt="Party"
                  className="entity-image"
                />
                <h3 className="entity-name">{party.abbreviation}</h3>
                <div className="button-container">
                  <button
                    className={`profile-button follow-button ${
                      isFollowing[party.party_id] ? "unfollow-button" : ""
                    }`}
                    onClick={() => handleFollowClick(party.party_id)}
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
                      {isFollowing[party.party_id] ? "Unfollow" : "Add to favourites"}
                    </span>
                  </button>
                  <button className="profile-button hide-button">
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
                    <span className="tooltip-text">Hide</span>
                  </button>
                  <button className="profile-button profile-button-large">
                    Vezi Profilul
                  </button>
                </div>
              </div>
              <div className="entity-details-second-part"></div>
            </div>
            <div className="articles-container">
              {party.articles.map((article, index) => (
                <Link
                  key={article.id}
                  to={`/article/${article.id}`}
                  className="article-link-entity"
                >
                  <div
                    className={`article-card-entity ${article.emotion.toLowerCase()} ${
                      index === party.articles.length - 1 ? "last-article" : ""
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
        ))}
      </div>
      <div className="statistics-section"></div>
    </div>
  );
};

export default PoliticalParties;
