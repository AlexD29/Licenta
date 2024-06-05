import React from 'react';
import './Navbar.css';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import SearchBar from './SearchBar';

function Navbar() {
  const location = useLocation();
  const isLogin = location.pathname === '/login';
  const isSignup = location.pathname === '/signup';
  const { isLoggedIn, logout } = useAuth();

  const handleLogout = () => {
    document.cookie = 'session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    logout();
  };

  const fetchSuggestions = async (query) => {
    try {
      const response = await fetch(`http://localhost:8000/api/suggestions?query=${query}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch suggestions');
      }
      const data = await response.json();
      console.log(data)
      return data;
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      return [];
    }
  }; 

  const handleSearch = (searchTerm) => {
    console.log(`Searching for: ${searchTerm}`);
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/">
          <img src="/icons/WDIVW_icon_logo.png" alt="Logo" />
        </Link>
      </div>
      <div className="navbar-text-logo">
        <Link to="/">
          <img src="/icons/WDIVW_text_logo.png" alt="Text Logo" />
        </Link>
      </div>
      { !isLogin && !isSignup && (
        <SearchBar onSearch={handleSearch} fetchSuggestions={fetchSuggestions}/>
      )}
      { !isLogin && !isSignup && (
      <div className="navbar-tabs">
        <ul>
          <li><Link to="/explore">Explorează</Link></li>
          <li><a href="#">Interesele tale</a></li>
          <li><a href="#">Despre</a></li>
          {isLoggedIn && (
            <li><Link to="/account">Cont</Link></li>
          )}
          {!isLoggedIn && (
            <li><Link to="/login">Login</Link></li>
          )}
        </ul>
      </div>
      )}
    </nav>
  );
}

export default Navbar;
