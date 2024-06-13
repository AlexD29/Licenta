import React, { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { formatDate } from "Articles";

const ArticlesList = ({ entity_id, entity_type, currentPage }) => {
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [totalArticles, setTotalArticles] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const articlesPerPage = 5;

  const fetchArticles = async (page) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/articles/${entity_type}/${entity_id}?page=${page}&limit=${articlesPerPage}`
      );
      const data = await response.json();
      window.scrollTo({ top: 0, behavior: "smooth" });
      if (response.ok) {
        setArticles(data.articles);
        setTotalArticles(data.total);
      } else {
        setError(data.error || "Failed to fetch articles");
      }
    } catch (error) {
      setError("Failed to fetch articles");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles(currentPage);
  }, [currentPage, entity_id, entity_type]);

  const handleNextPage = () => {
    if (currentPage < Math.ceil(totalArticles / articlesPerPage)) {
      const nextPage = currentPage + 1;
      navigate(`/${entity_type}/${entity_id}/page/${nextPage}`);
      fetchArticles(nextPage);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      const prevPage = currentPage - 1;
      navigate(`/${entity_type}/${entity_id}/page/${prevPage}`);
      fetchArticles(prevPage);
    }
  };

  if (loading) {
    return <div>Loading articles...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="second-part">
      <div className="articles-part">
        {articles.map((article) => (
          <Link
            key={article.id}
            to={`/article/${article.id}`}
            className="article-link-minimized"
          >
            <div
              className={`article-card-minimized ${article.emotion.toLowerCase()}`}
            >
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
            currentPage >= Math.ceil(totalArticles / articlesPerPage)
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
  );
};

export default ArticlesList;
