import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import './ArticleDetail.css';
import Footer from 'D:/Documents/Facultate/Licenta/app/my-react-app/src/Footer';
import SourceArticlesCountsWaterfallChart from 'charts/Source/ArticlesCountsWaterfallChart';
import ArticlesLastWeekChart from 'charts/Politician/ArticlesLastWeekChart';

function ArticleDetail() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/article/${id}`);
        setArticle(response.data.article);
        window.scrollTo(0, 0);
      } catch (error) {
        console.error('Error fetching article details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [id]);

  function formatDate(dateString) {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      // Format for today's date
      const options = { hour: 'numeric', minute: 'numeric', hour12: false };
      return `Astăzi, ${date.toLocaleTimeString('ro-RO', options)}`;
    } else if (date.toDateString() === yesterday.toDateString()) {
      // Format for yesterday's date
      const options = { hour: 'numeric', minute: 'numeric', hour12: false };
      return `Ieri, ${date.toLocaleTimeString('ro-RO', options)}`;
    } else {
      // Format the date to desired format, e.g., "19 aprilie 2024, 15:30"
      const dateFormat = { day: 'numeric', month: 'long', year: 'numeric' }; // Change '2-digit' to 'numeric'
      const timeFormat = { hour: 'numeric', minute: 'numeric', hour12: false };
      const formattedDate = date.toLocaleDateString('ro-RO', dateFormat);
      const formattedTime = date.toLocaleTimeString('ro-RO', timeFormat);
      return `${formattedDate}, ${formattedTime}`;
    }
  }

  function getNumberOfViews(article) {
    if (article.source === 'Digi24' || article.source === 'PROTV') {
      return article.source + " doesn't provide views.";
    } else {
      return article.number_of_views ? `Number of Views: ${article.number_of_views}` : 'N/A';
    }
  }
  
  function getNumberOfComments(article) {
    if (article.source === 'Digi24' || article.source === 'PROTV' || article.source === 'Mediafax') {
      return article.source + " doesn't provide comments.";
    } else {
      return article.comments.length > 0 ? `Number of Comments: ${article.comments.length}` : 'There are no comments at the moment.';
    }
  }

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

  return (
    <div>
      <div className='main-container-article-details'>
        <div className='first-part'>
          <SourceArticlesCountsWaterfallChart sourceId={9}/>
        </div>
        <div className="article-container">
          <h1 className="article-title">{article.title}</h1>
          <div className="article-big-image-div">
              <img src={article.image_url} alt="Article" className="article-big-image" />
          </div>
          <div className="article-info">
            <p><strong>Autor:</strong> {article.author}</p>
            <p><strong>Data publicării:</strong> {formatDate(article.published_date)}</p>
            <p><strong>{getNumberOfViews(article)}</strong></p>
            <p><strong>{getNumberOfComments(article)}</strong></p>
          </div>
          <div className="article-content">
            <p>
              {article.article_text && Array.isArray(article.article_text) ?
                article.article_text.map(paragraph => paragraph.split(/\s+/)).flat().slice(0, maxWords).join(' ') :
                "Article text not available"
              }
              {article.article_text && Array.isArray(article.article_text) && article.article_text.flatMap(paragraph => paragraph.split(/\s+/)).length > maxWords && '...'}
              <span className="fade-out"></span>
            </p>
          </div>
          <a href={article.url} className="full-article-button" target="_blank" rel="noopener noreferrer">Articolul Complet</a>
          <div className='article-info'>
            <div className="tag-list">
              {article.tags.map((tag, index) => (
                <Link key={index} to={`/tags/${tag}`} className="tag-link">{tag}</Link>
              ))}
            </div>
            <div className="first-article-source-image">
              <img src={article.source_image_url} alt={article.source_name} className="details-source-icon" />
            </div>
            <div>
              <p>{article.emotion}</p>
            </div>
          </div>
          
        </div>
        <div className='third-part'>
          <ArticlesLastWeekChart />
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default ArticleDetail;
