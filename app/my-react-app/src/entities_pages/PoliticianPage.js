// src/components/PoliticianPage.js
import React, { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './EntityPage.css';
import Footer from '../Footer';

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
      const dateFormat = { day: 'numeric', month: 'long', year: 'numeric' };
      return date.toLocaleDateString('ro-RO', dateFormat);
    }
  }  
  
const PoliticianPage = () => {
  const { id } = useParams();
  const [politician, setPolitician] = useState(null);
  
  useEffect(() => {
    const fetchPolitician = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/politician/${id}`);
        setPolitician(response.data);
        
      } catch (error) {
        console.error("Error fetching politician:", error);
      }
    };
    fetchPolitician();
  }, [id]);

  if (!politician) return <div>Loading...</div>;

  console.log(politician);

  return (
    <div className="entity-page">
        <div className='entity-first-part'>
            <div className='picture-div politician'>
                <img src={politician.image_url} alt={`${politician.first_name} ${politician.last_name}`} className='entity-profile-picture'/>
                <p className='politician-position'>{politician.position}</p>
                <div className='political-party-card'>
                    <img src={politician.political_party_image_url} className='political-party-image'></img>
                </div>
                <div className='politician-description'>
                    <h3>Descriere</h3>
                    <p>{politician.description}</p>
                </div>
                
            </div>
            <h1 className='profile-name-element'>{politician.first_name} {politician.last_name}</h1>
            <p className='profile-name-element'>Locuiește în {politician.city}</p>
            <p className='profile-name-element'>Născut pe {formatDate(politician.date_of_birth)} - {politician.age} de ani</p>
        </div>
        <div className='entity-second-part'>
            <div className='first-part'></div>
            <div className='second-part'>
                <div className='articles-part'>
                {politician.articles.map((article) => (
                    <Link key={article.id} to={`/article/${article.id}`} className="article-link-minimized">
                        <div className={`article-card-minimized ${article.emotion.toLowerCase()}`}>
                            <div className="article-image-div-minimized">
                                <img src={article.image_url} className="article-image-minimized" />
                            </div>
                            <div className="article-details-div-minimized">
                                <h3 className="article-text-minimized">{article.title}</h3>
                                <p className="article-text-minimized">{formatDate(article.published_date)}</p>
                            </div>
                            <div className="article-source-image-minimized">
                                <img src={article.source_image_url} alt={article.source_name} className="source-icon-minimized" />
                            </div>
                        </div>
                    </Link>
                ))}
                </div>
            </div>
        </div>
        <Footer/>
    </div>
  );  
};

export default PoliticianPage;
