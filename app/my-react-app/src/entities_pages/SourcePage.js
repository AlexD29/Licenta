import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import "./EntityPage.css";
import Footer from "../Footer";
import ArticlesList from "./ArticlesList";

const SourcePage = ({ userId }) => {
  const { id, page } = useParams();
  const currentPage = parseInt(page, 10) || 1;
  const [source, setSource] = useState(null);

  useEffect(() => {
    const fetchSource = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/source/${id}`,
          {
            params: { user_id: userId || null },
          }
        );
        setSource(response.data);
      } catch (error) {
        console.error("Error fetching source:", error);
      }
    };
    fetchSource();
  }, [userId, id]);

  if (!source) return <div>Loading...</div>;

  return (
    <div className="container">
      <div className="entity-page-first-part">
        <div className="entity-first-part-centered">
          <div className="background-div source"></div>
          <div className="profile-info">
            <div className="info-first-column">
              <img
                src={source.image_url}
                alt={source.name}
                className="entity-profile-picture source-picture"
              />
              <h1 className="profile-name">{source.name}</h1>
            </div>
            <div className="info-second-column">
              <div className="source-description">
                <h3>About</h3>
                <p>{source.description}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="entity-second-part">
        <div className="first-part"></div>
        <ArticlesList entity_id={id} entity_type="source" currentPage={currentPage} />
      </div>
      <Footer />
    </div>
  );
};

export default SourcePage;
