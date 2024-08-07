import React, { useEffect, useState, useMemo } from "react";
import axios from "axios";
import { useParams, Link } from "react-router-dom";
import "./ArticleDetail.css";
import Footer from "D:/Documents/Facultate/Licenta/app/my-react-app/src/Footer";
import RelatedEntityCard from "charts/ArticleDetails/RelatedEntityCard";
import { truncateTitle, formatDate } from "Articles";
import ArticleAnalytics from "charts/ArticleDetails/ArticleAnalytics";
import EntityPairComponent from "charts/ArticleDetails/EntityPairComponent";

function ArticleDetail({ userId }) {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [relatedEntities, setRelatedEntities] = useState([]);
  const [articleSuggestions, setArticleSuggestions] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [favoritesLoaded, setFavoritesLoaded] = useState(false);

  useEffect(() => {
    const fetchFavorites = async () => {
      if (!userId) {
        console.warn("User ID not available yet. Cannot fetch favorites.");
        return;
      }
      try {
        const response = await axios.get(
          `http://localhost:8000/api/favorites?user_id=${userId}`
        );
        setFavorites(response.data);
        setFavoritesLoaded(true); // Indicate that favorites have been loaded
      } catch (error) {
        console.error("Error fetching favorites:", error);
      }
    };

    fetchFavorites();
  }, [userId]);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/article/${id}`
        );
        setArticle(response.data.article);
        window.scrollTo(0, 0);
      } catch (error) {
        console.error("Error fetching article details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [id]);

  useEffect(() => {
    const fetchRelatedEntities = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/related-entities/${id}`
        );
        setRelatedEntities(response.data.related_entities);
        setLoading(false);
      } catch (err) {
        setLoading(false);
      }
    };

    fetchRelatedEntities();
  }, [id]);

  useEffect(() => {
    const fetchArticleSuggestions = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/article-suggestions/${id}`
        );
        setArticleSuggestions(response.data.suggested_articles);
      } catch (error) {
        console.error("Error fetching article suggestions:", error);
      }
    };

    fetchArticleSuggestions();
  }, [id]);

  const maxWords = 100;

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!article) {
    return <div>Failed to load article.</div>;
  }

  const groupedEntities = relatedEntities.reduce((acc, entity) => {
    if (!acc[entity.entity_type]) {
        acc[entity.entity_type] = [];
    }
    acc[entity.entity_type].push(entity);
    return acc;
}, {});

// Generate all possible pairs
const pairs = [];

// Generate pairs of entities with the same entity_type
Object.values(groupedEntities).forEach(entities => {
    for (let i = 0; i < entities.length - 1; i++) {
        for (let j = i + 1; j < entities.length; j++) {
            pairs.push([entities[i], entities[j]]);
        }
    }
});

// Generate pairs of entities with different entity_types
const entityTypes = Object.keys(groupedEntities);

for (let i = 0; i < entityTypes.length - 1; i++) {
    const type1 = entityTypes[i];
    for (let j = i + 1; j < entityTypes.length; j++) {
        const type2 = entityTypes[j];
        const entities1 = groupedEntities[type1];
        const entities2 = groupedEntities[type2];

        for (const entity1 of entities1) {
            for (const entity2 of entities2) {
                pairs.push([entity1, entity2]);
            }
        }
    }
}


  const emotionTranslations = {
    Positive: "Pozitiv",
    Negative: "Negativ",
    Neutral: "Neutru",
  };

  const emotion = emotionTranslations[article.emotion] || article.emotion;


  const shuffledEntities = [...relatedEntities].sort(() => 0.5 - Math.random());

  // Create RelatedEntityCard components
  const entityCards = shuffledEntities.map(entity => (
    <RelatedEntityCard
      key={`${entity.entity_type}-${entity.entity_id}`}
      entityType={entity.entity_type}
      entityName={entity.entity_name}
      entityImage={entity.image_url}
      entityId={entity.entity_id}
      favorites={favorites}
      userId={userId}
    />
  ));

  // Combine all components into one array
  const allComponents = [
    ...entityCards,
    <ArticleAnalytics key="article-analytics" articleId={id} emotion={article.emotion} />,
    pairs.length > 0 ? <EntityPairComponent key="entity-pair" pairs={pairs} /> : null,
  ].filter(Boolean); // Filter out any null values

  // Shuffle the combined components array
  const shuffledComponents = allComponents.sort(() => 0.5 - Math.random());

  // Split the shuffled components into two parts
  const midpoint = Math.ceil(shuffledComponents.length / 2);
  const firstPartComponents = shuffledComponents.slice(0, midpoint);
  const thirdPartComponents = shuffledComponents.slice(midpoint);

  const totalComponents = shuffledComponents.length;
  const additionalClass = totalComponents < 5 ? 'not-enough' : '';

  return (
    <div>
      <div className="main-container-article-details">
        <div className={`first-part ${additionalClass}`}>
          {firstPartComponents}
        </div>
        <div className="article-container">
          <div className={`emotion-bar ${article.emotion.toLowerCase()}-bar`}>
            <p className="emotion-text">{emotion}</p>
          </div>
          <h1 className="article-title">{article.title}</h1>
          <div className="article-big-image-div">
            <img
              src={article.image_url}
              alt="Article"
              className="article-big-image"
            />
          </div>
          <div className="article-info">
            <div className="article-details-date-div">
              <svg
                className="date-svg-details"
                id="Layer_1"
                data-name="Layer 1"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 512 512"
              >
                <title>Date</title>
                <path d="M464.3,103.08a64,64,0,0,0-59-39.08H362.67A21.34,21.34,0,0,0,320,64H192a21.34,21.34,0,0,0-42.67,0H106.67a63.94,63.94,0,0,0-64,64V405.33a63.94,63.94,0,0,0,64,64H405.33a63.94,63.94,0,0,0,64-64V128A63.7,63.7,0,0,0,464.3,103.08ZM426.67,405.33a21.36,21.36,0,0,1-21.34,21.34H106.67a21.36,21.36,0,0,1-21.34-21.34v-192H426.67Zm0-234.66H85.33V128a21.36,21.36,0,0,1,21.34-21.33h42.66a21.34,21.34,0,0,0,42.67,0H320a21.34,21.34,0,0,0,42.67,0h42.66A21.36,21.36,0,0,1,426.67,128Z"></path>
                <path d="M149.36,278.39l0,.52c0,.17,0,.35.05.52l.06.52c0,.17,0,.35.07.52s.05.35.08.52.07.34.1.51.07.34.11.51l.12.51c0,.17.09.34.14.5s.09.34.14.51.11.33.16.5.11.33.17.49l.18.49.2.48c.06.16.13.32.2.48l.22.48.23.47.24.46.25.46.26.45c.09.15.18.3.28.45l.28.44.29.43.31.42.32.42c.1.14.21.27.32.41s.23.27.34.4l.35.4.35.38.37.38c.13.12.25.25.38.36s.25.25.38.36l.4.35.4.34.41.32.42.32.42.31.43.29.44.28.45.28.45.26.46.25.46.24.47.23.48.22.48.2.48.2.49.18.49.17.5.16.5.14.51.14.51.12.51.11.51.1.52.08.52.07.52.06.52.05.52,0,.53,0h1.05l.53,0,.52,0,.52-.05.53-.06.51-.07.52-.08.52-.1.5-.11.51-.12.51-.14.5-.14.5-.16.49-.17.49-.18.49-.2.48-.2.47-.22.47-.23.46-.24.46-.25.45-.26.45-.28.44-.28.43-.29.43-.31.41-.32.41-.32.41-.34.39-.35c.13-.11.26-.24.38-.36s.26-.24.38-.36l.37-.38.36-.38.34-.4c.12-.13.23-.26.34-.4l.33-.41.31-.42.31-.42.29-.43.29-.44.27-.45c.09-.15.18-.3.26-.45s.17-.31.25-.46a5.06,5.06,0,0,0,.24-.46l.23-.47c.08-.16.15-.32.22-.48l.21-.48.19-.48.18-.49c.06-.16.12-.33.17-.49s.11-.34.16-.5l.15-.51c0-.16.09-.33.13-.5l.12-.51c0-.17.08-.34.11-.51s.07-.34.1-.51.06-.35.08-.52.05-.35.08-.52,0-.34,0-.52,0-.35.05-.52l0-.52c0-.18,0-.36,0-.53s0-.35,0-.53,0-.35,0-.52,0-.35,0-.53l0-.52c0-.18,0-.35-.05-.53s0-.34,0-.52-.05-.34-.08-.51,0-.35-.08-.52-.06-.34-.1-.52-.07-.34-.11-.51l-.12-.51c0-.16-.09-.33-.13-.5l-.15-.5c0-.17-.1-.33-.16-.5s-.11-.33-.17-.49l-.18-.49-.19-.49-.21-.48c-.07-.15-.14-.31-.22-.47s-.15-.32-.23-.47a4,4,0,0,0-.24-.46c-.08-.16-.16-.31-.25-.46s-.17-.31-.26-.45l-.27-.45c-.09-.15-.19-.29-.29-.44l-.29-.43c-.1-.14-.2-.29-.31-.43l-.31-.41-.33-.41-.34-.41-.34-.39-.36-.39-.37-.37c-.12-.13-.25-.25-.38-.37l-.38-.36-.39-.34-.41-.34-.41-.33-.41-.31-.43-.31-.43-.29-.44-.29-.45-.27-.45-.26-.46-.25-.46-.25-.47-.22-.47-.22-.48-.21-.49-.19-.49-.18-.49-.17-.5-.16-.5-.15-.51-.13-.51-.12-.5-.11-.52-.1-.52-.08-.51-.08-.53-.06-.52,0-.52,0-.53,0h-1.05l-.53,0-.52,0-.52,0-.52.06-.52.08-.52.08-.51.1-.51.11-.51.12-.51.13-.5.15-.5.16-.49.17-.49.18-.48.19-.48.21-.48.22-.47.22-.46.25-.46.25-.45.26-.45.27-.44.29-.43.29-.42.31-.42.31-.41.33-.4.34-.4.34-.38.36-.38.37-.37.37-.35.39-.35.39-.34.41c-.11.13-.22.27-.32.41s-.22.27-.32.41l-.31.43-.29.43-.28.44c-.1.15-.19.3-.28.45s-.17.3-.26.45-.17.3-.25.46l-.24.46c-.08.15-.16.31-.23.47s-.15.32-.22.47-.14.32-.2.48-.13.33-.2.49l-.18.49c-.06.16-.11.33-.17.49s-.11.33-.16.5-.1.33-.14.5-.1.34-.14.5l-.12.51c0,.17-.07.34-.11.51s-.07.35-.1.52-.05.34-.08.52,0,.34-.07.51l-.06.52c0,.18,0,.35-.05.53l0,.52c0,.18,0,.35,0,.53s0,.35,0,.52,0,.36,0,.53S149.35,278.21,149.36,278.39Z"></path>
                <path d="M234.69,278.39c0,.17,0,.34,0,.52s0,.35,0,.52l.06.52c0,.17,0,.35.07.52l.09.52.09.51c0,.17.08.34.11.51s.08.34.13.51.08.34.13.5l.15.51.15.5.18.49a4.84,4.84,0,0,0,.18.49c.06.16.12.32.19.48l.21.48.21.48c.08.15.15.31.23.47l.24.46.25.46c.09.15.18.3.26.45l.28.45.28.44.3.43.3.42.32.42.33.41.33.4.35.4.36.38.37.38c.12.12.24.25.37.36l.39.36.39.35.4.34.41.32.42.32.42.31.44.29c.14.1.29.19.44.28s.29.19.44.28l.45.26.46.25.47.24.47.23.47.22.48.2.48.2.49.18.5.17.49.16.51.14.5.14.51.12.51.11.52.1.51.08.52.07.52.06.52.05.53,0,.52,0h1.06l.52,0,.53,0,.52-.05.52-.06.52-.07.51-.08.52-.1.51-.11.51-.12.5-.14.5-.14.5-.16.49-.17.49-.18.49-.2.48-.2.47-.22.47-.23.47-.24.45-.25.46-.26c.15-.09.3-.18.44-.28s.3-.18.44-.28l.43-.29.43-.31.42-.32.41-.32.4-.34.39-.35.39-.36c.13-.11.25-.24.37-.36l.37-.38.36-.38.35-.4.33-.4.33-.41.32-.42.3-.42.3-.43.28-.44c.09-.15.19-.3.27-.45l.27-.45.25-.46.24-.46c.08-.16.15-.32.22-.47s.15-.32.22-.48l.21-.48c.07-.16.13-.32.19-.48a4.84,4.84,0,0,0,.18-.49l.18-.49.15-.5.15-.51c.05-.16.09-.33.13-.5s.09-.34.13-.51.07-.34.11-.51L277,281l.09-.52c0-.17,0-.35.07-.52l.06-.52c0-.17,0-.35,0-.52s0-.35,0-.52,0-.36,0-.53v-1.05c0-.18,0-.35,0-.53s0-.35,0-.52,0-.35,0-.53l-.06-.52c0-.17-.05-.34-.07-.51l-.09-.52-.09-.52c0-.17-.08-.34-.11-.51s-.08-.34-.13-.51-.08-.33-.13-.5l-.15-.5-.15-.5-.18-.49a4.09,4.09,0,0,0-.18-.49c-.06-.16-.12-.33-.19-.49l-.21-.48c-.07-.15-.14-.31-.22-.47s-.14-.32-.22-.47l-.24-.46c-.08-.16-.17-.31-.25-.46l-.27-.45c-.08-.15-.18-.3-.27-.45l-.28-.44-.3-.43-.3-.43c-.11-.14-.21-.28-.32-.41l-.33-.41-.33-.41-.35-.39-.36-.39-.37-.37-.37-.37-.39-.36-.39-.34-.4-.34-.41-.33-.42-.31-.43-.31c-.14-.1-.28-.2-.43-.29l-.44-.29L267,259c-.15-.09-.3-.18-.46-.26s-.3-.17-.45-.25l-.47-.25-.47-.22-.47-.22-.48-.21-.49-.19-.49-.18-.49-.17-.5-.16-.5-.15-.5-.13-.51-.12-.51-.11-.52-.1-.51-.08-.52-.08-.52-.06-.52,0-.53,0-.52,0h-1.06l-.52,0-.53,0-.52,0-.52.06-.52.08-.51.08-.52.1-.51.11-.51.12-.5.13-.51.15-.49.16-.5.17-.49.18-.48.19-.48.21-.47.22-.47.22-.47.25-.46.25L245,259l-.44.27-.44.29-.44.29-.42.31-.42.31-.41.33-.4.34-.39.34-.39.36-.37.37-.37.37-.36.39-.35.39-.33.41-.33.41c-.11.13-.21.27-.32.41l-.3.43-.3.43-.28.44-.28.45-.26.45c-.08.15-.17.3-.25.46l-.24.46c-.08.15-.15.31-.23.47l-.21.47-.21.48c-.07.16-.13.33-.19.49a4.09,4.09,0,0,0-.18.49l-.18.49-.15.5-.15.5c0,.17-.09.34-.13.5s-.09.34-.13.51-.07.34-.11.51l-.09.52-.09.52c0,.17-.05.34-.07.51l-.06.52c0,.18,0,.35,0,.53s0,.35,0,.52,0,.35,0,.53v1.05C234.68,278,234.68,278.21,234.69,278.39Z"></path>
                <path d="M320,278.39l0,.52c0,.17,0,.35,0,.52l.06.52c0,.17,0,.35.08.52s.05.35.08.52.06.34.1.51.07.34.11.51l.12.51c0,.17.09.34.13.5l.15.51c.05.16.1.33.16.5s.11.33.17.49l.18.49.19.48.21.48c.07.16.14.32.22.48s.15.31.22.47.16.31.25.46.16.31.25.46.17.3.26.45l.27.45.29.44.29.43.31.42.31.42.33.41c.11.14.22.27.34.4l.34.4.36.38.37.38c.12.12.25.25.38.36s.25.25.38.36l.39.35.41.34.41.32.41.32.43.31.43.29.44.28.45.28.45.26.46.25.46.24.47.23.47.22.48.2.49.2.49.18.49.17.5.16.5.14.51.14.5.12.51.11.52.1.52.08.51.07.53.06.52.05.52,0,.53,0h1.05l.53,0,.52,0,.52-.05.52-.06.52-.07.52-.08.51-.1.51-.11.51-.12.51-.14.5-.14.5-.16.49-.17.49-.18.48-.2.48-.2.48-.22.47-.23.46-.24.46-.25.45-.26.45-.28.44-.28.43-.29.42-.31.42-.32.41-.32.4-.34.4-.35.38-.36c.13-.11.25-.24.38-.36s.25-.25.36-.38l.36-.38.35-.4c.11-.13.23-.26.34-.4s.22-.27.32-.41l.32-.42.31-.42.29-.43.28-.44c.1-.15.19-.3.28-.45l.26-.45.25-.46.24-.46.23-.47.22-.48c.07-.16.14-.32.2-.48l.2-.48.18-.49c.06-.16.11-.33.17-.49s.11-.34.16-.5.1-.34.14-.51.1-.33.14-.5l.12-.51c0-.17.07-.34.11-.51s.07-.34.1-.51,0-.35.08-.52.05-.35.07-.52l.06-.52c0-.17,0-.35.05-.52l0-.52c0-.18,0-.36,0-.53s0-.35,0-.53,0-.35,0-.52,0-.35,0-.53l0-.52c0-.18,0-.35-.05-.53l-.06-.52c0-.17,0-.34-.07-.51s-.05-.35-.08-.52-.07-.34-.1-.52-.07-.34-.11-.51l-.12-.51c0-.16-.09-.33-.14-.5s-.09-.34-.14-.5-.11-.33-.16-.5-.11-.33-.17-.49l-.18-.49c-.07-.16-.13-.33-.2-.49s-.13-.32-.2-.48-.15-.31-.22-.47-.15-.32-.23-.47l-.24-.46c-.08-.16-.17-.31-.25-.46s-.17-.31-.26-.45-.18-.3-.28-.45l-.28-.44-.29-.43-.31-.43c-.1-.14-.21-.28-.32-.41s-.21-.28-.32-.41l-.34-.41-.35-.39c-.11-.13-.24-.26-.36-.39l-.36-.37-.38-.37-.38-.36-.4-.34-.4-.34-.41-.33-.42-.31-.42-.31-.43-.29-.44-.29-.45-.27-.45-.26-.46-.25-.46-.25-.47-.22-.48-.22-.48-.21-.48-.19-.49-.18-.49-.17-.5-.16-.5-.15-.51-.13-.51-.12-.51-.11-.51-.1-.52-.08-.52-.08-.52-.06-.52,0-.52,0-.53,0h-1.05l-.53,0-.52,0-.52,0-.53.06-.51.08-.52.08-.52.1-.51.11-.5.12-.51.13-.5.15-.5.16-.49.17-.49.18-.49.19-.48.21-.47.22-.47.22-.46.25-.46.25-.45.26-.45.27-.44.29-.43.29-.43.31-.41.31-.41.33-.41.34-.39.34-.38.36c-.13.12-.26.24-.38.37l-.37.37-.36.39-.34.39-.34.41-.33.41-.31.41c-.11.14-.21.29-.31.43l-.29.43c-.1.15-.2.29-.29.44l-.27.45c-.09.14-.18.3-.26.45s-.17.3-.25.46-.17.3-.25.46-.15.31-.22.47-.15.32-.22.47l-.21.48-.19.49-.18.49c-.06.16-.12.33-.17.49s-.11.33-.16.5l-.15.5c0,.17-.09.34-.13.5l-.12.51c0,.17-.08.34-.11.51s-.07.35-.1.52-.06.34-.08.52-.05.34-.08.51l-.06.52c0,.18,0,.35,0,.53l0,.52c0,.18,0,.35,0,.53s0,.35,0,.52,0,.36,0,.53S320,278.21,320,278.39Z"></path>
                <path d="M149.36,363.72l0,.52c0,.18,0,.35.05.52l.06.53c0,.17,0,.34.07.51s.05.35.08.52.07.34.1.52.07.34.11.51l.12.5c0,.17.09.34.14.51s.09.34.14.5.11.33.16.5.11.33.17.49l.18.49c.07.16.13.33.2.49s.13.32.2.48.15.31.22.47.15.32.23.47l.24.46c.08.16.17.31.25.46l.26.45.27.45.29.44.29.43.31.43c.1.14.21.28.32.41s.21.28.32.41l.34.41.35.39c.11.13.23.26.35.38l.37.38.38.37.38.36.4.34.4.34.41.33.42.31.42.31.43.29.44.29.45.27.45.26.46.25a5.06,5.06,0,0,0,.46.24l.47.23.48.22.48.21.48.19.49.18.49.17.5.16.5.15.51.13.51.12.51.11.51.1.52.08.52.08.52.06.52,0,.52,0,.53,0h1.05l.53,0,.52,0,.52,0,.53-.06.51-.08.52-.08.52-.1.51-.11.5-.12.51-.13.5-.15.5-.16.49-.17.49-.18.49-.19.48-.21.47-.22.47-.23a4,4,0,0,0,.46-.24l.46-.25.45-.26.45-.27.44-.29.43-.29.43-.31.41-.31.41-.33.41-.34.39-.34.38-.36c.13-.12.26-.24.38-.37s.25-.25.37-.38l.36-.38.34-.39.34-.41.33-.41.31-.41c.11-.14.21-.29.31-.43l.29-.43c.1-.15.2-.29.29-.44l.27-.45c.09-.15.18-.3.26-.45s.17-.3.25-.46.17-.3.25-.46.15-.31.22-.47.15-.32.22-.47l.21-.48.19-.49.18-.49c.06-.16.12-.33.17-.49s.11-.33.16-.5l.15-.5c0-.17.09-.34.13-.51l.12-.5c0-.17.08-.34.11-.51s.07-.35.1-.52.06-.34.08-.52.05-.34.08-.51l.06-.53c0-.17,0-.34,0-.52l0-.52c0-.18,0-.35,0-.53s0-.35,0-.52,0-.36,0-.53,0-.35,0-.53l0-.52c0-.17,0-.35,0-.52l-.06-.52c0-.18-.05-.35-.08-.52s0-.35-.08-.52-.06-.34-.1-.51-.07-.34-.11-.51l-.12-.51c0-.17-.09-.34-.13-.51l-.15-.5c0-.16-.1-.33-.16-.5s-.11-.33-.17-.49l-.18-.49-.19-.48-.21-.48c-.07-.16-.14-.32-.22-.48s-.15-.31-.22-.47-.16-.31-.25-.46-.16-.31-.25-.46-.17-.3-.26-.45l-.27-.45-.29-.44-.29-.43-.31-.42-.31-.42-.33-.41c-.11-.14-.22-.27-.34-.4l-.34-.4-.36-.38-.37-.38-.38-.37-.38-.35-.39-.35-.41-.34-.41-.32-.41-.32-.43-.31-.43-.29-.44-.29-.45-.27-.45-.26-.46-.25-.46-.24-.47-.23-.47-.22-.48-.2-.49-.2-.49-.18-.49-.17-.5-.16-.5-.14-.51-.14-.5-.12-.51-.11-.52-.1-.52-.08-.51-.07-.53-.06-.52-.05-.52,0-.53,0h-1.05l-.53,0-.52,0-.52.05-.52.06-.52.07-.52.08-.51.1-.51.11-.51.12-.51.14-.5.14-.5.16-.49.17-.49.18-.48.2-.48.2-.48.22-.47.23-.46.24-.46.25-.45.26-.45.27-.44.29-.43.29-.42.31-.42.32-.41.32-.4.34-.4.35-.38.35-.38.37-.37.38c-.12.13-.24.25-.35.38l-.35.4c-.11.13-.23.26-.34.4s-.22.27-.32.41l-.32.42-.31.42-.29.43c-.1.15-.19.3-.29.44l-.27.45-.26.45c-.08.15-.17.3-.25.46l-.24.46-.23.47-.22.48c-.07.15-.14.32-.2.48l-.2.48-.18.49c-.06.16-.11.33-.17.49s-.11.34-.16.5-.1.34-.14.5-.1.34-.14.51l-.12.51c0,.17-.07.34-.11.51s-.07.34-.1.51-.05.35-.08.52,0,.34-.07.52l-.06.52c0,.17,0,.35-.05.52l0,.52c0,.18,0,.36,0,.53s0,.35,0,.53,0,.35,0,.52S149.35,363.54,149.36,363.72Z"></path>
                <path d="M234.69,363.72c0,.17,0,.35,0,.52s0,.35,0,.52l.06.53c0,.17,0,.34.07.51l.09.52.09.52c0,.17.08.34.11.51s.08.34.13.5.08.34.13.51l.15.5.15.5.18.49a4.09,4.09,0,0,0,.18.49c.06.16.12.33.19.49l.21.48.21.47c.08.16.15.32.23.47l.24.46c.08.16.17.31.25.46s.18.3.26.45l.28.45.28.44.3.43.3.43c.11.14.21.28.32.41l.33.41.33.41.35.39.36.38c.12.13.24.26.37.38l.37.37.39.36.39.34.4.34.41.33.42.31.42.31.44.29.44.29.44.27.45.26.46.25a5.21,5.21,0,0,0,.47.24l.47.23.47.22.48.21.48.19.49.18.5.17.49.16.51.15.5.13.51.12.51.11.52.1.51.08.52.08.52.06.52,0,.53,0,.52,0h1.06l.52,0,.52,0,.53,0,.52-.06.52-.08.51-.08.52-.1.51-.11.51-.12.5-.13.5-.15.5-.16.49-.17.49-.18.49-.19.48-.21.47-.22.47-.23a5.21,5.21,0,0,0,.47-.24c.15-.08.31-.16.45-.25s.31-.17.46-.26l.44-.27.44-.29c.15-.09.29-.19.43-.29l.43-.31.42-.31.41-.33.4-.34.39-.34.39-.36.37-.37c.13-.12.25-.25.37-.38l.36-.38.35-.39.33-.41.33-.41c.11-.13.21-.27.32-.41l.3-.43.3-.43.28-.44c.09-.15.19-.3.27-.45l.27-.45c.08-.15.17-.3.25-.46l.24-.46c.08-.15.15-.31.22-.47s.15-.32.22-.47l.21-.48c.07-.16.13-.33.19-.49a4.09,4.09,0,0,0,.18-.49l.18-.49.15-.5.15-.5c.05-.17.09-.34.13-.51s.09-.33.13-.5.07-.34.11-.51l.09-.52.09-.52c0-.17,0-.34.07-.51l.06-.53c0-.17,0-.34,0-.52s0-.35,0-.52,0-.35,0-.53v-1.05c0-.17,0-.35,0-.53s0-.34,0-.52,0-.35,0-.52l-.06-.52c0-.18-.05-.35-.07-.52L277,359l-.09-.51c0-.17-.08-.34-.11-.51s-.08-.34-.13-.51-.08-.34-.13-.51l-.15-.5-.15-.5-.18-.49a4.84,4.84,0,0,0-.18-.49c-.06-.16-.12-.32-.19-.48l-.21-.48c-.07-.16-.14-.32-.22-.48s-.14-.31-.22-.47l-.24-.46c-.08-.16-.17-.31-.25-.46l-.27-.45c-.08-.15-.18-.3-.27-.45l-.28-.44-.3-.43-.3-.42-.32-.42-.33-.41-.33-.4-.35-.4-.36-.38-.37-.38-.37-.37-.39-.35-.39-.35-.4-.34-.41-.32-.42-.32-.43-.31-.43-.29-.44-.29-.44-.27c-.15-.09-.3-.18-.46-.26l-.45-.25-.47-.24-.47-.23-.47-.22-.48-.2-.49-.2-.49-.18-.49-.17-.5-.16-.5-.14-.5-.14-.51-.12-.51-.11-.52-.1-.51-.08-.52-.07-.52-.06-.53-.05-.52,0-.52,0h-1.06l-.52,0-.53,0-.52.05-.52.06-.52.07-.51.08-.52.1-.51.11-.51.12-.5.14-.51.14-.49.16-.5.17-.49.18-.48.2-.48.2-.47.22-.47.23-.47.24-.46.25-.45.26-.44.27-.44.29-.44.29-.42.31-.42.32-.41.32-.4.34-.39.35-.39.35-.37.37-.37.38-.36.38-.35.4-.33.4-.33.41-.32.42-.3.42-.3.43-.28.44-.28.45c-.08.15-.17.3-.26.45s-.17.3-.25.46l-.24.46c-.08.16-.15.32-.23.47l-.21.48-.21.48c-.07.16-.13.32-.19.48a4.84,4.84,0,0,0-.18.49l-.18.49-.15.5-.15.5c0,.17-.09.34-.13.51s-.09.34-.13.51-.07.34-.11.51L235,359l-.09.52c0,.17-.05.34-.07.52l-.06.52c0,.17,0,.35,0,.52s0,.35,0,.52,0,.36,0,.53v1.05C234.68,363.37,234.68,363.54,234.69,363.72Z"></path>
              </svg>
              <p className="date-text-details">
                {formatDate(article.published_date)}
              </p>
            </div>
            <div className="article-details-author-div">
              <svg
                className="author-svg"
                version="1.1"
                xmlns="http://www.w3.org/2000/svg"
                x="0px"
                y="0px"
                viewBox="0 0 64 64"
              >
                <g id="Layer_1"></g>
                <g id="Layer_2">
                  <g>
                    <path
                      d="M32,36c4.1,0,7.5-3.4,7.5-7.5s-3.4-7.5-7.5-7.5s-7.5,3.4-7.5,7.5S27.9,36,32,36z M32,23c3,0,5.5,2.5,5.5,5.5
                    c0,3-2.5,5.5-5.5,5.5c-3,0-5.5-2.5-5.5-5.5C26.5,25.5,29,23,32,23z"
                    ></path>
                    <path
                      d="M51.8,32c0-10.9-8.9-19.8-19.8-19.8C21.1,12.1,12.2,21,12.2,32c0,5.6,2.3,10.9,6.4,14.6l0,0.1l0.6,0.5
                    c3.6,3.1,8.2,4.7,12.9,4.7c4.7,0,9.3-1.7,12.9-4.7l0.6-0.5l0-0.1C49.5,42.8,51.8,37.5,51.8,32z M14.1,32c0-9.9,8-17.9,17.9-17.9
                    c9.9,0,17.9,8,17.9,17.9c0,4.8-1.9,9.3-5.3,12.6c-2.3-4.7-7.2-7.9-12.6-7.9c-5.4,0-10.3,3.1-12.6,7.9C16,41.3,14.1,36.7,14.1,32z
                    M32,49.8c-4,0-7.8-1.3-10.9-3.8c1.9-4.3,6.2-7.1,10.9-7.1c4.7,0,9.1,2.8,10.9,7.1C39.8,48.4,36,49.8,32,49.8z"
                    ></path>
                  </g>
                </g>
              </svg>
              <p className="author-text-details">{article.author}</p>
            </div>
            <div className="first-article-source-image">
              <Link
                className="source-image-link"
                to={`/source/${article.source_id}`}
              >
                <img
                  src={article.source_image_url}
                  alt={article.source_name}
                  className="details-source-icon"
                />
              </Link>
            </div>
          </div>
          <div className="article-content">
            <p>
              {article.article_text && Array.isArray(article.article_text)
                ? article.article_text
                    .map((paragraph) => paragraph.split(/\s+/))
                    .flat()
                    .slice(0, maxWords)
                    .join(" ")
                : "Article text not available"}
              {article.article_text &&
                Array.isArray(article.article_text) &&
                article.article_text.flatMap((paragraph) =>
                  paragraph.split(/\s+/)
                ).length > maxWords &&
                "..."}
              <span className="fade-out"></span>
            </p>
          </div>
          <a
            href={article.url}
            className="full-article-button"
            target="_blank"
            rel="noopener noreferrer"
          >
            Articolul Complet
          </a>
          <div className="article-info-tags">
            <div className="tag-list">
              {article.tags.map((tag, index) => (
                <div className="tag-link">{tag}</div>
              ))}
            </div>
          </div>
        </div>
        <div className={`third-part ${additionalClass}`}>
          {thirdPartComponents}
        </div>
      </div>
      <hr className="article-details-hr" />
      <div className="article-suggestions">
        <h2 className="article-suggestions-title">Articole similare</h2>
        <div className="suggested-articles-container">
          {articleSuggestions.length > 0 ? (
            articleSuggestions.map((article) => (
              <Link
                key={article.id}
                to={`/article/${article.id}`}
                className="suggested-article-link"
              >
                <div
                  className={`suggested-article-card ${article.emotion.toLowerCase()}`}
                >
                  <div className="suggested-article-image-div">
                    <img
                      src={article.image_url}
                      alt={article.title}
                      className="suggested-article-image"
                    />
                  </div>
                  <div className="suggested-article-details">
                    <h3 className="suggested-article-title">
                      {truncateTitle(article.title, 100)}
                    </h3>
                    <div className="article-suggestion-source-div">
                      <img
                        className="article-suggestion-source"
                        src={article.source.image_url}
                      ></img>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          ) : (
            <p>No suggested articles found.</p>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default ArticleDetail;
