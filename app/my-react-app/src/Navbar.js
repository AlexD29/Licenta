import React from 'react';
import './Navbar.css';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

function Navbar() {
  const location = useLocation();
  const isLogin = location.pathname === '/login';
  const isSignup = location.pathname === '/signup';
  const { isLoggedIn, logout } = useAuth();

  const handleLogout = () => {
    document.cookie = 'session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    logout();
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
        <div className="navbar-search">
          <input type="text" placeholder="Caută..." />
        </div>
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
