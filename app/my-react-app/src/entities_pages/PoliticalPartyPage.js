import React, { useEffect, useState, useMemo } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { shuffle } from 'lodash';
import "./EntityPage.css";
import Footer from "../Footer";
import ArticlesList from "./ArticlesList";
import EntityRankComponent from "charts/Politician/EntityRankComponent";
import NegativeSources from "charts/Politician/NegativeSources";
import PositiveSources from "charts/Politician/PositiveSources";
import TopPoliticalPartyAuthorsPieChart from "charts/Political Parties/TopPoliticalPartyAuthorsPieChart";
import PoliticalPartyArticlesDistribution from "charts/Political Parties/PoliticalPartyArticlesDistribution";
import PoliticalPartyArticlesChart from "charts/Political Parties/PoliticalPartyArticlesChart";
import PoliticianSourcesChart from "charts/Politician/PoliticianSourcesChart";
import PoliticalPartyTopEntities from "charts/Political Parties/PoliticalPartyTopEntities";

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

const getIdeologies = (ideology) => {
  if (!ideology) return [];

  return ideology.split(',').map((ideologyItem, index) => (
    <div key={index} className="ideology-item">
      {ideologyItem.trim()}
    </div>
  ));
};

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

  const charts = useMemo(() => {
    if (!political_party) return [];
    return [
      <PoliticalPartyArticlesDistribution politicalPartyId={id} />,
      <PoliticalPartyArticlesChart politicalPartyId={id} />,
      <PoliticianSourcesChart entityId={id} entityType="political-party" />,
      <NegativeSources entityId={id} entityType="political-party" />,
      <PositiveSources entityId={id} entityType="political-party" />,
      <PoliticalPartyTopEntities politicalPartyId={id} />,
      <TopPoliticalPartyAuthorsPieChart politicalPartyId={id} />,
      <EntityRankComponent entityId={id} entityType='political_party' />
    ];
  }, [id, political_party]);

  const shuffledCharts = useMemo(() => {
    const shuffled = shuffle(charts);
    return {
      firstPart: shuffled.slice(0, 4),
      thirdPart: shuffled.slice(4, 8)
    };
  }, [charts]);

  console.log(political_party);

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
              <div className="profile-icon-plus-text">
                <span>
                  <svg
                    className="profile-svg"
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
                </span>
                Fondat în {political_party.founded_year}
              </div>
            </div>
            <div className="info-second-column">
                <div className="second-column-first-row">
                  <div className="entity-big-text political-party-option">{political_party.full_name}<br></br><span className="entity-secondary-text">Partid de {political_party.position}</span></div>
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
                <div className="second-column-second-row">
                  {getIdeologies(political_party.ideology)}
                </div>
                <div className="politician-description">
                    <h3>Despre</h3>
                    <p>{political_party.description}</p>
                </div>
            </div>
          </div>
        </div>
      </div>
      <div className="entity-middle-part">
          <div className="middle-bar-box">
            <span>Total articole în 2024</span>
            <span className="category-value">{political_party.total_articles}</span>
          </div>
          <div className="middle-bar-box positive-text">
            <span>Pozitive</span>
            <span className="category-value">{political_party.positive_articles}</span>
          </div>
          <div className="middle-bar-box negative-text">
            <span>Negative</span>
            <span className="category-value">{political_party.negative_articles}</span>
          </div>
          <div className="middle-bar-box neutral-text">
            <span>Neutre</span>
            <span className="category-value">{political_party.neutral_articles}</span>
          </div>
      </div>
      <div className="entity-second-part">
          <div className="first-part">
            {shuffledCharts.firstPart.map((chart, index) => (
              <div key={index} className="chart-container">
                {chart}
              </div>
            ))}
          </div>
          <ArticlesList entity_id={id} entity_type="political-party" currentPage={currentPage} />
          <div className="third-part">
            {shuffledCharts.thirdPart.map((chart, index) => (
              <div key={index} className="chart-container">
                {chart}
              </div>
            ))}
          </div>
      </div>
      <Footer />
    </div>
  );
};

export default PoliticalPartyPage;
