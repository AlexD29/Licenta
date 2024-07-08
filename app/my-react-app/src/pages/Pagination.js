import React from "react";
import { Link } from "react-router-dom";

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };


  return (
    <nav className="pagination gutter-col-xs-0">
      <div className="flex flex-middle">
        <div className="col-3">
          <Link
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-link pagination-link-prev"
            rel="prev"
          >
            <svg
              width="100%"
              height="100%"
              viewBox="0 0 16 16"
              version="1.1"
              style={{ fillRule: "evenodd", clipRule: "evenodd", strokeLinejoin: "round", strokeMiterlimit: 2 }}
            >
              <g id="Icon">
                <path d="M11.53,13.47l-5.469,-5.47c-0,-0 5.469,-5.47 5.469,-5.47c0.293,-0.292 0.293,-0.768 0,-1.06c-0.292,-0.293 -0.768,-0.293 -1.06,-0l-6,6c-0.293,0.293 -0.293,0.767 -0,1.06l6,6c0.292,0.293 0.768,0.293 1.06,0c0.293,-0.292 0.293,-0.768 0,-1.06Z"></path>
              </g>
            </svg>
          </Link>
        </div>
        <span className="current-page">{currentPage}</span>
        <div className="col-3 col-end">
          <Link
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="pagination-link pagination-link-next"
          >
            <svg
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
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Pagination;
