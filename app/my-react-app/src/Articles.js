import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link, useParams } from 'react-router-dom';
import './Articles.css';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import Footer from './Footer';
import TodayPiechart from './charts/TodayPiechart';

function Articles() {
  const [articles, setArticles] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  const { page } = useParams();
  const pageNumber = parseInt(page, 10) || 1;

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/articles?page=${pageNumber}&limit=${20}`);
        setArticles(response.data.articles);
        setTotalPages(response.data.totalPages);
        setCurrentPage(parseInt(page, 10) || 1);
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchArticles();
  }, [page]);

  useEffect(() => {
    // window.scrollTo(0, 0);
  }, [currentPage, pageNumber]);
  

  const renderPagination = () => {
    let pages = [];
  
    // Display the current page
    pages.push(
      <Link 
        key={currentPage} 
        to={`/page/${currentPage}`} 
        className={`pagination-link ${currentPage === currentPage ? 'pagination-link-current' : ''}`}
      >
        {currentPage}
      </Link>
    );
  
    // Display the next two pages
    if (currentPage < totalPages) {
      pages.push(
        <Link 
          key={currentPage + 1} 
          to={`/page/${currentPage + 1}`} 
          className="pagination-link"
        >
          {currentPage + 1}
        </Link>
      );
    }
  
    if (currentPage < totalPages - 1) {
      pages.push(
        <Link 
          key={currentPage + 2} 
          to={`/page/${currentPage + 2}`} 
          className="pagination-link"
        >
          {currentPage + 2}
        </Link>
      );
    }
  
    // Display dots if there are more than 3 pages left after the current page
    if (currentPage < totalPages - 2) {
      pages.push(<span key="dots" className='pagination-dots'>...</span>);
    }
  
    // Display the last three pages
    if (currentPage < totalPages) {
      pages.push(
        <Link 
          key={totalPages - 2} 
          to={`/page/${totalPages - 2}`} 
          className="pagination-link"
        >
          {totalPages - 2}
        </Link>
      );
    }
  
    if (currentPage < totalPages - 1) {
      pages.push(
        <Link 
          key={totalPages - 1} 
          to={`/page/${totalPages - 1}`} 
          className="pagination-link"
        >
          {totalPages - 1}
        </Link>
      );
    }
  
    if (currentPage < totalPages) {
      pages.push(
        <Link 
          key={totalPages} 
          to={`/page/${totalPages}`} 
          className="pagination-link"
        >
          {totalPages}
        </Link>
      );
    }
  
    return pages;
  };

  const getSourceIcon = (source, className) => {
    switch (source) {
      case 'Ziare.com':
        return <img src="/source_icons/ziaredotcom_logo.png" alt="ziaredotcom" className={className} />;
      case 'PROTV':
        return <img src="/source_icons/protv_logo.png" alt="protv" className={className} />;
      case 'Digi24':
        return <img src="/source_icons/digi24_logo.png" alt="digi24" className={className} />;
      case 'Mediafax':
        return <img src="/source_icons/mediafax_logo.jpg" alt="mediafax" className={className} />;
      case 'Adevarul':
        return <img src="/source_icons/adevarul_logo.jpeg" alt="adevarul" className={className} />;
      case 'Observator':
        return <img src="/source_icons/observator_logo.png" alt="observator" className={className} />;
      case 'HotNews':
        return <img src="/source_icons/hotnews_logo.png" alt="hotnews" className={className} />;
      case 'Stiri pe surse':
        return <img src="/source_icons/stiripesurse_logo.png" alt="stiripesurse" className={className} />;
      case 'Gândul':
        return <img src="/source_icons/gandul_logo.jpeg" alt="gandul" className={className} />;
      case 'Bursa':
        return <img src="/source_icons/bursa_logo.jpg" alt="bursa" className={className} />;
      case 'Antena 3':
        return <img src="/source_icons/antena3_logo.jpg" alt="antena3" className={className} />;
      default:
        return <span>{source}</span>;
    }
  };  

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
    
  const [firstArticle, ...otherArticles] = articles;


  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-animation"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!articles) {
    return <div>No articles to show.</div>;
  }

  return (
  <div className="main-container">
    <div className="home-container">
        <div className="home-first-part">
            <div className="home-left-side">
                {firstArticle && (
                    <Link key={firstArticle.id} to={`/article/${firstArticle.id}`} className="article-link">
                      <div className="first-article-card">
                        <div className="first-article-image-div">
                          <img src={firstArticle.image_url} alt={"image"} className="first-article-image" />
                        </div>
                        <div className="first-article-details-div">
                          <h3 className="article-text">{firstArticle.title}</h3>
                          <p className="article-text">{formatDate(firstArticle.published_date)}</p>
                          <div className="first-article-source-image">
                            {getSourceIcon(firstArticle.source, "first-article-source-icon")}
                          </div>
                        </div>
                      </div>
                    </Link>
                  )}
            </div>
            <div className="home-right-side">
              <TodayPiechart />
            </div>
        </div>
        <div className="home-second-part">
          {otherArticles.map((article) => (
            <Link key={article.id} to={`/article/${article.id}`} className="article-link">
              <div className={`article-card ${article.emotion.toLowerCase()}`}>
                <div className="article-image-div">
                  <img src={article.image_url} className="article-image" />
                </div>
                <div className="article-details-div">
                  <h3 className="article-text">{article.title}</h3>
                  <p className="article-text">{formatDate(article.published_date)}</p>
                </div>
                <div className="article-source-image">
                  {getSourceIcon(article.source, "source-icon")}
                </div>
              </div>
            </Link>
          ))}
        </div>
        </div>
        <nav className="pagination gutter-col-xs-0">
          <div className="flex flex-middle">
            <div className="col-3">
              <Link to={`/page/1`} className="pagination-link pagination-link-prev">
              <svg version="1.1" id="Layer_1" x="0px" y="0px" width="92px" height="92px" viewBox="0 0 92 92" enableBackground="new 0 0 92 92" >
                <path id="XMLID_646_" d="M78.7,9.4c-1.4-0.7-3-0.5-4.2,0.5L33,42.9c-1,0.8-1.5,1.9-1.5,3.1s0.6,2.4,1.5,3.1l41.5,33
                c0.7,0.6,1.6,0.9,2.5,0.9c0.6,0,1.2-0.1,1.7-0.4c1.4-0.7,2.3-2.1,2.3-3.6V13C81,11.5,80.1,10.1,78.7,9.4z M73,70.7L41.9,46L73,21.3
                V70.7z M19,14.6v63.5c0,2.5-2,4.5-4.5,4.5s-4.5-2-4.5-4.5V14.6c0-2.5,2-4.5,4.5-4.5S19,12.1,19,14.6z"></path>
              </svg>
              </Link>
              <Link to={`/page/${currentPage > 1 ? currentPage - 1 : 1}`} className="pagination-link pagination-link-prev" rel="prev">
                <svg width="100%" height="100%" viewBox="0 0 16 16" version="1.1" style={{ fillRule: 'evenodd', clipRule: 'evenodd', strokeLinejoin: 'round', strokeMiterlimit: 2 }}>
                  <g id="Icon">
                    <path d="M11.53,13.47l-5.469,-5.47c-0,-0 5.469,-5.47 5.469,-5.47c0.293,-0.292 0.293,-0.768 0,-1.06c-0.292,-0.293 -0.768,-0.293 -1.06,-0l-6,6c-0.293,0.293 -0.293,0.767 -0,1.06l6,6c0.292,0.293 0.768,0.293 1.06,0c0.293,-0.292 0.293,-0.768 0,-1.06Z"></path>
                  </g>
                </svg>
              </Link>
            </div>
            <div className="col-6 col-center">
              {renderPagination()}
            </div>
            <div className="col-3 col-end">
              <Link to={`/page/${currentPage < totalPages ? currentPage + 1 : totalPages}`} className="pagination-link pagination-link-next">
              <svg version="1.1" id="Layer_1" x="0px" y="0px" viewBox="0 0 32 32" style={{ enableBackground: 'new 0 0 32 32' }}>
                <g>
                  <path d="M11.5,26c-0.3,0-0.5-0.1-0.7-0.3c-0.4-0.4-0.4-1,0-1.4l8.3-8.3l-8.3-8.3c-0.4-0.4-0.4-1,0-1.4s1-0.4,1.4,0l9,9
                  c0.4,0.4,0.4,1,0,1.4l-9,9C12,25.9,11.8,26,11.5,26z"></path>
                </g>
              </svg>
              </Link>
              <Link to={`/page/${totalPages}`} className="pagination-link pagination-link-next" rel="next">
                <svg version="1.1" id="Layer_1" x="0px" y="0px" width="92px" height="92px" viewBox="0 0 92 92" enableBackground="new 0 0 92 92" xmlSpace="preserve">
                  <path id="XMLID_659_" d="M59.5,42.9l-42-33c-1.2-0.9-2.8-1.1-4.2-0.5C11.9,10.1,11,11.5,11,13v66c0,1.5,0.9,2.9,2.3,3.6
                  c0.6,0.3,1.2,0.4,1.7,0.4c0.9,0,1.8-0.3,2.5-0.9l42-33c1-0.8,1.5-1.9,1.5-3.1C61,44.8,60.4,43.6,59.5,42.9z M19,70.8V21.2L50.5,46
                  L19,70.8z M81,14.6v63.5c0,2.5-2,4.5-4.5,4.5s-4.5-2-4.5-4.5V14.6c0-2.5,2-4.5,4.5-4.5S81,12.1,81,14.6z"></path>
                </svg>
              </Link>
            </div>
          </div>
        </nav>
        <Footer />
    </div>
  );
}

export default Articles;
