import React, { useState, useEffect, useRef } from 'react';
import './Navbar.css';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import SearchBar from './SearchBar';

const scrollToTheTop = () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
};

function removeDomainFromEmail(email) {
  if (typeof email !== 'string') {
    throw new TypeError('The provided input must be a string');
  }
  const atIndex = email.indexOf('@');
  if (atIndex === -1) {
    return email;
  }
  return email.substring(0, atIndex);
}

export { scrollToTheTop };

function Navbar({ email }) {
  const location = useLocation();
  const isLogin = location.pathname === '/login';
  const isSignup = location.pathname === '/signup';
  const { isLoggedIn, logout } = useAuth();
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const dropdownRef = useRef(null);

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

  const toggleDropdown = () => {
    setDropdownVisible(!dropdownVisible);
  };

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownVisible(false);
    }
  };

  useEffect(() => {
    if (dropdownVisible) {
      document.addEventListener('click', handleClickOutside);
    } else {
      document.removeEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [dropdownVisible]);

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/">
          <img src="/icons/WDIVW_icon_logo.png" alt="Logo" />
        </Link>
      </div>
      <div className="navbar-text-logo">
        <Link className='logo-link' to="/">
          <img src="/icons/WDIVW_text_logo.png" alt="Text Logo" />
        </Link>
      </div>
      {!isLogin && !isSignup && (
        <SearchBar onSearch={handleSearch} fetchSuggestions={fetchSuggestions} />
      )}
      {!isLogin && !isSignup && (
        <div className="navbar-tabs">
          <ul>
            <li><Link to="/explore" className='navbar-list-elements'>Explorează</Link></li>
            <li><a href="/my-interests" className='navbar-list-elements'>Interesele tale</a></li>
            <li><a href="/about" className='navbar-list-elements'>Despre</a></li>
            {isLoggedIn ? (
              <li ref={dropdownRef} onClick={toggleDropdown} className='navbar-list-elements dropdown'>
                Cont
                {dropdownVisible && (
                  <ul className="dropdown-menu">
                    <li><Link className='logout-link' to="/account">{removeDomainFromEmail(email)}</Link></li>
                    <li onClick={handleLogout}><Link className='logout-link' to="/login">Logout</Link></li>
                  </ul>
                )}
              </li>
            ) : (
              <li><Link to="/login" className='navbar-list-elements'>Login</Link></li>
            )}
          </ul>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
