import React, { useState, useEffect } from "react";

const truncateTitle = (title, maxLength) => {
  if (title.length > maxLength) {
    return title.slice(0, maxLength) + "...";
  }
  return title;
};

const SuggestionsList = ({ suggestions }) => (
  <ul className="suggestions-list">
    {suggestions.map((suggestion, index) => (
      <li key={index} className="suggestion-item">
        {suggestion.category === "Politician" ? (
          <>
            <img
              className="suggestion-icon"
              src={suggestion.image_url}
              alt={`${suggestion.first_name} ${suggestion.last_name}`}
            />
            <div className="suggestion-name-div">
              <span>
                {suggestion.first_name} {suggestion.last_name}
              </span>
            </div>
            <div className="suggestion-category-div">
              <span>{suggestion.category}</span>
            </div>
          </>
        ) : suggestion.category === "Partid politic" ? (
          <>
            <img
              className="suggestion-icon"
              src={suggestion.image_url}
              alt={`${suggestion.abbreviation}`}
            />
            <div className="suggestion-name-div">
              <span>{suggestion.abbreviation}</span>
            </div>
            <div className="suggestion-category-div">
              <span>{suggestion.category}</span>
            </div>
          </>
        ) : suggestion.category === "Oraș" ? (
          <>
            <img
              className="suggestion-icon"
              src={suggestion.image_url}
              alt={`${suggestion.name}`}
            />
            <div className="suggestion-name-div">
              <span>{suggestion.name}</span>
            </div>
            <div className="suggestion-category-div">
              <span>{suggestion.category}</span>
            </div>
          </>
        ) : suggestion.category === "Tag" ? (
          <>
            <svg className="suggestion-tag" viewBox="0 0 53.33 64">
              <defs></defs>
              <title>Asset 73</title>
              <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                  <path
                    className="cls-1"
                    d="M50.67,64A2.69,2.69,0,0,1,49,63.44L26.67,46.05,4.3,63.44A2.66,2.66,0,0,1,0,61.33V8A8,8,0,0,1,8,0H45.33a8,8,0,0,1,8,8V61.33A2.66,2.66,0,0,1,50.67,64Zm-24-24a2.68,2.68,0,0,1,1.63.56L48,55.88V8a2.68,2.68,0,0,0-2.67-2.67H8A2.68,2.68,0,0,0,5.33,8V55.88L25,40.56A2.69,2.69,0,0,1,26.67,40Z"
                  ></path>
                </g>
              </g>
            </svg>
            <div className="suggestion-name-div">
              <span>{suggestion.tag_text}</span>
            </div>
            <div className="suggestion-category-div">
              <span>{suggestion.category}</span>
            </div>
          </>
        ) : suggestion.category === "Article" ? (
          <>
            <img
              className="article-suggestion-icon"
              src={suggestion.image_url}
              alt={`${suggestion.title}`}
            />
            <div className="article-suggestion-name-div">
              <span>{truncateTitle(suggestion.title, 90)}</span>
            </div>
          </>
        ) : (
          <>
            <div className="suggestion-category-div">
              <span>{suggestion.category}</span>
            </div>
          </>
        )}
      </li>
    ))}
  </ul>
);

const SearchBar = ({ fetchSuggestions }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [inputFocused, setInputFocused] = useState(false);

  const handleInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  useEffect(() => {
    const fetchAndSetSuggestions = async () => {
      if (searchTerm.length >= 3) {
        const results = await fetchSuggestions(searchTerm);
        setSuggestions(results);
      } else {
        setSuggestions([]);
      }
    };

    fetchAndSetSuggestions();
  }, [searchTerm, fetchSuggestions]);

  const handleSearch = (event) => {
    event.preventDefault();
    console.log(`Searching for: ${searchTerm}`);
  };

  return (
    <div className="navbar-search">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Caută..."
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setInputFocused(true)}
          onBlur={() => setInputFocused(false)}
          className="search-input"
        />
        <button type="submit" className="search-button">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="feather feather-search"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </button>
      </form>
      {inputFocused && suggestions.length > 0 && (
        <SuggestionsList suggestions={suggestions} />
      )}
    </div>
  );
};

export default SearchBar;
