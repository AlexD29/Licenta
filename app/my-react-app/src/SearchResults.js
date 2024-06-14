import React, { useEffect, useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import './SearchResults.css';

const formatDate = (dateString) => {
  // Implement your date formatting logic here
  return dateString; // Placeholder implementation
};

const SearchResults = () => {
  const [results, setResults] = useState(null);
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const query = searchParams.get('query');

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/search?query=${query}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Error fetching search results:', error);
      }
    };

    if (query) {
      fetchResults();
    }
  }, [query]);

  if (!results) {
    return <div>Loading...</div>;
  }

  // Define the desired order of categories
  const categoryOrder = [
    'politicians',
    'political_parties',
    'cities',
    'sources',
    'elections',
    'articles'
  ];

  return (
    <div className='results-page'>
        <div className='results-text-div'>
            <h1>Search Results for "{query}"</h1>
        </div>
        <div className='results-div'>
            <div className='first-part'>

            </div>
            <div className="second-part">
        {categoryOrder.map((category) => (
            <div key={category}>
            {category === 'articles' && results[category] && results[category].length > 0 && (
                <div className="articles-part">
                    {results[category].map((article) => (
                    <Link
                        key={article.id}
                        to={`/article/${article.id}`}
                        className={`article-link-minimized ${article.emotion.toLowerCase()}`}
                    >
                        <div className="article-card-minimized">
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
                        <div className="article-source-image-minimized">
                            <img
                            src={article.source_image_url}
                            alt={article.source_name}
                            className="source-icon-minimized"
                            />
                        </div>
                        </div>
                    </Link>
                    ))}
                </div>
            )}
            </div>
        ))}
        </div>
        </div>
    </div>
  );
};

export default SearchResults;
