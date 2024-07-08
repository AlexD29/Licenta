import React, { useEffect, useState } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import './SearchResults.css';
import { formatDate } from 'Articles';
import { formatPopulation } from 'entities_pages/CityPage';
import { calculateRemainingDays } from 'pages/Elections';
import Footer from 'Footer';
import PoliticianSourcesChart from 'charts/Politician/PoliticianSourcesChart';
import PoliticianArticlesDistribution from 'charts/Politician/PoliticianArticlesDistribution';

const SearchResults = () => {
  const [results, setResults] = useState(null);
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const query = searchParams.get('query');
  const pageParam = searchParams.get('page');

  let initialPage = parseInt(pageParam);
  if (isNaN(initialPage) || initialPage <= 0) {
    initialPage = 1;
  }

  const [currentPage, setCurrentPage] = useState(initialPage);
  const articlesPerPage = 10;
  const [totalResults, setTotalResults] = useState(0);
  const navigate = useNavigate();

  const fetchResults = async (page) => {
    try {
      console.log('Fetching results for page:', page);
      const response = await fetch(`http://localhost:8000/api/search?query=${query}&page=${page}&limit=${articlesPerPage}`);
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      window.scrollTo({ top: 0, behavior: "smooth" });
      const data = await response.json();
      
      setResults(data.results);
      setTotalResults(data.totalResults);
      
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };
  
  useEffect(() => {
    if (query) {
      fetchResults(currentPage);
    }
  }, [query, currentPage]);

  const handleNextPage = () => {
      const nextPage = currentPage + 1;
      setCurrentPage(nextPage);
      navigate(`/search?query=${query}&page=${nextPage}`);
      fetchResults(nextPage);
  };
  
  const handlePrevPage = () => {
      const prevPage = currentPage - 1;
      setCurrentPage(prevPage); // Update currentPage in state
      navigate(`/search?query=${query}&page=${prevPage}`);
      fetchResults(prevPage);
  };


  const electionDates = {
    'Alegeri Europarlamentare': new Date('2024-06-09'),
    'Alegeri Locale': new Date('2024-06-09'),
    'Alegeri Prezidențiale': new Date('2024-09-15'),
    'Alegeri Parlamentare': new Date('2024-12-08')
};

const normalizeString = (str) => {
    return str
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, '-');
  };

  if (!results) {
    return <div>Loading...</div>;
  }

  const categoryOrder = [
    'Politician',
    'Partid politic',
    'Oraș',
    'Sursă',
    'Alegeri',
    'articles'
  ];

  return (
    <div className='results-page'>
      <div className='results-text-div'>
        <h1>Rezultatele căutării pentru "{query}"</h1>
        <p>Rezultate totale: {totalResults}</p>
      </div>
      <div className='results-div'>
        <div className='first-part'>
        </div>
        <div className="second-part">
            {categoryOrder.map((category) => (
                category !== 'articles' && results.some(item => item.category === category) && (
                <div key={category}>
                <ul className='entities-list'>
                    {results.filter(item => item.category === category).map((item) => (
                    <li key={item.id}>
                        {category === 'Politician' && (
                        <div className='entities-part'>
                            <Link 
                            key={item.id}
                            to={`/politician/${item.id}`}
                            className="entity-link-minimized"
                            >
                            <div className='entity-card-minimized'>
                                <div className="entity-image-div-minimized">
                                <img
                                    src={item.image_url}
                                    className="entity-image-minimized"
                                    alt=""
                                />
                                </div>
                                <div className="entity-details-div-minimized">
                                <h3 className="entity-text-minimized">{item.first_name} {item.last_name}</h3>
                                <p className="article-text-minimized">
                                    {item.position}
                                </p>
                                </div>
                            </div>
                            </Link>
                        </div>
                        )}
                        {category === 'Partid politic' && (
                        <div className='entities-part'>
                            <Link 
                            key={item.id}
                            to={`/political-party/${item.id}`}
                            className="entity-link-minimized"
                            >
                            <div className='entity-card-minimized'>
                                <div className="entity-image-div-minimized">
                                <img
                                    src={item.image_url}
                                    className="political-party-image-minimized"
                                    alt=""
                                />
                                </div>
                                <div className="entity-details-div-minimized">
                                <h3 className="entity-text-minimized">{item.abbreviation}</h3>
                                <p className="article-text-minimized">
                                    {item.full_name}
                                </p>
                                </div>
                            </div>
                            </Link>
                        </div>
                        )}
                        {category === 'Oraș' && (
                        <div className='entities-part'>
                            <Link 
                            key={item.id}
                            to={`/city/${item.id}`}
                            className="entity-link-minimized"
                            >
                            <div className='entity-card-minimized'>
                                <div className="entity-image-div-minimized">
                                <img
                                    src={item.image_url}
                                    className="entity-image-minimized"
                                    alt=""
                                />
                                </div>
                                <div className="entity-details-div-minimized">
                                <h3 className="entity-text-minimized">{item.name}</h3>
                                <p className="article-text-minimized">
                                    {formatPopulation(item.population)} de locuitori
                                </p>
                                </div>
                            </div>
                            </Link>
                        </div>
                        )}
                        {category === 'Alegeri' && (
                        <div className='entities-part'>
                            <Link 
                            key={item.id}
                            to={`/alegeri/${normalizeString(item.name)}`}
                            className="entity-link-minimized"
                            >
                            <div className='entity-card-minimized'>
                                <div className="entity-image-div-minimized">
                                <img
                                    src={item.image_url}
                                    className="entity-image-minimized"
                                    alt=""
                                />
                                </div>
                                <div className="entity-details-div-minimized">
                                <h3 className="entity-text-minimized">{item.name}</h3>
                                {electionDates[item.name] && (
                                    <p className="category-description">
                                    {calculateRemainingDays(electionDates[item.name])} zile rămase
                                    </p>
                                )}
                                </div>
                            </div>
                            </Link>
                        </div>
                        )}
                        {category === 'Sursă' && (
                        <div className='entities-part'>
                            <Link 
                            key={item.id}
                            to={`/source/${item.id}`}
                            className="entity-link-minimized"
                            >
                            <div className='entity-card-minimized'>
                                <div className="entity-image-div-minimized">
                                <img
                                    src={item.image_url}
                                    className="political-party-image-minimized"
                                    alt=""
                                />
                                </div>
                                <div className="entity-details-div-minimized source-details-div">
                                <h3 className="entity-text-minimized">{item.name}</h3>
                                </div>
                            </div>
                            </Link>
                        </div>
                        )}
                    </li>
                    ))}
                </ul>
                </div>
                )
            ))}
            {results.map(item => {
            if (item.category === 'Article') {
                const article = item;
                return (
                <Link
                    key={article.id}
                    to={`/article/${article.id}`}
                    className="article-link-minimized"
                >
                    <div className={`article-card-minimized ${article.emotion.toLowerCase()}`}>
                    <div className="article-image-div-minimized">
                        <img
                        src={article.image_url}
                        className="article-image-minimized"
                        alt=""
                        />
                    </div>
                    <div className="article-details-div-minimized">
                        <h3 className="article-text-minimized">{article.title}</h3>
                        <p className="article-text-minimized">
                        {formatDate(article.published_date)}
                        </p>
                    </div>
                    {/* Assuming article.source is available */}
                    <div className="article-source-image-minimized">
                        <img
                        src={article.source.image_url}
                        alt={article.source.name}
                        className="source-icon-minimized"
                        />
                    </div>
                    </div>
                </Link>
                );
            }})}
            <div className="pagination">
                <button
                onClick={handlePrevPage}
                disabled={currentPage === 1}
                className="page-nav"
                >
                <svg
                    className="pagination-svg"
                    width="100%"
                    height="100%"
                    viewBox="0 0 16 16"
                    version="1.1"
                    style={{
                    fillRule: "evenodd",
                    clipRule: "evenodd",
                    strokeLinejoin: "round",
                    strokeMiterlimit: 2,
                    }}
                >
                    <g id="Icon">
                    <path d="M11.53,13.47l-5.469,-5.47c-0,-0 5.469,-5.47 5.469,-5.47c0.293,-0.292 0.293,-0.768 0,-1.06c-0.292,-0.293 -0.768,-0.293 -1.06,-0l-6,6c-0.293,0.293 -0.293,0.767 -0,1.06l6,6c0.292,0.293 0.768,0.293 1.06,0c0.293,-0.292 0.293,-0.768 0,-1.06Z"></path>
                    </g>
                </svg>
                </button>
                <span className="current-page">{currentPage}</span>
                <button
                onClick={handleNextPage}
                disabled={
                    currentPage >= Math.ceil(totalResults / articlesPerPage)
                }
                className="page-nav"
                >
                <svg
                    className="pagination-svg"
                    version="1.1"
                    id="Layer_1"
                    x="0px"
                    y="0px"
                    viewBox="0 0 32 32"
                    style={{ enableBackground: "new 0 0 32 32" }}
                >
                    <g>
                    <path
                        d="M11.5,26c-0.3,0-0.5-0.1-0.7-0.3c-0.4-0.4-0.4-1,0-1.4l8.3-8.3l-8.3-8.3c-0.4-0.4-0.4-1,0-1.4s1-0.4,1.4,0l9,9
                    c0.4,0.4,0.4,1,0,1.4l-9,9C12,25.9,11.8,26,11.5,26z"
                    ></path>
                    </g>
                </svg>
                </button>
            </div>
        </div>
        <div className='third-part'>
        </div>
      </div>
      <Footer/>
    </div>
  );
  
};

export default SearchResults;
