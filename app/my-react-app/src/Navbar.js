import React from 'react';
import './Navbar.css';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();

  const isLogin = location.pathname === '/login';
  const isSignup = location.pathname === '/signup';
  // window.scrollTo(0, 0);

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
          <input type="text" placeholder="Search..." />
        </div>
      )}
      { !isLogin && !isSignup && (
        <div className="navbar-tabs">
          <ul>
            <li><a href="#">Explore</a></li>
            <li><a href="#">Your_Interests</a></li>
            <li><a href="#">About</a></li>
            {!isLogin && <li><Link to="/login">Login</Link></li>}
          </ul>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
