import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./EntityPage.css";
import Footer from "../Footer";
import ArticlesList from "./ArticlesList";

function formatDate(dateString) {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);

  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return `Astăzi`;
  } else if (date.toDateString() === yesterday.toDateString()) {
    return `Ieri`;
  } else {
    const dateFormat = { day: "numeric", month: "long", year: "numeric" };
    return date.toLocaleDateString("ro-RO", dateFormat);
  }
}

const PoliticalPartyPage = ({ userId }) => {
  const { id, page } = useParams();
  const currentPage = parseInt(page, 10) || 1;
  const [political_party, setParty] = useState(null);

  useEffect(() => {
    const fetchParty = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/political-party/${id}`,
          {
            params: { user_id: userId || null },
          }
        );
        setParty(response.data);
        console.log(political_party);
      } catch (error) {
        console.error("Error fetching political_party:", error);
      }
    };
    fetchParty();
  }, [userId, id]);

  const handleAddFavorite = async (political_party) => {
    try {
      if (!userId) {
        alert("You need to log in to add favorites.");
        return;
      }

      const action = political_party.isFavorite ? "remove" : "add";

      await axios.post("http://localhost:8000/api/favorites", {
        user_id: userId,
        entity_id: political_party.id,
        entity_type: political_party.entity_type,
        action: action,
      });
      setParty({ ...political_party, isFavorite: !political_party.isFavorite });
    } catch (error) {
      console.error("Error updating favorites:", error);
    }
  };

  if (!political_party) return <div>Loading...</div>;

  return (
    <div className="container">
      <div className="entity-page-first-part">
        <div className="entity-first-part-centered">
          <div className="background-div political-party"></div>
          <div className="profile-info">
            <div className="info-first-column">
              <img
                src={political_party.image_url}
                alt={political_party.abbreviation}
                className="entity-profile-picture political-party-picture"
              />
              <h1 className="profile-name">{political_party.abbreviation}</h1>
              <p className="profile-birth">
                Fondat la {formatDate(political_party.founded_date)}
              </p>
            </div>
            <div className="info-second-column">
                <div className="second-column-first-row">
                  <div className="entity-big-text">{political_party.full_name}</div>
                  <div className="profile-button-div-political-party">
                      <button
                          className={`follow-button-profile ${
                          !userId
                              ? "inactive"
                              : political_party.isFavorite
                              ? "remove"
                              : "add"
                          }`}
                          onClick={() => handleAddFavorite(political_party)}
                          disabled={!userId}
                      >
                          {political_party.isFavorite ? "Nu mai urmări" : "Urmarește"}
                      </button>
                  </div>
                </div>
                <div className="politician-description">
                    <h3>Despre</h3>
                    <p>{political_party.description}</p>
                </div>
            </div>
          </div>
        </div>
      </div>
      <div className="entity-second-part">
          <div className="first-part"></div>
          <ArticlesList entity_id={id} entity_type="political-party" currentPage={currentPage} />
      </div>
      <Footer />
    </div>
  );
};

export default PoliticalPartyPage;
