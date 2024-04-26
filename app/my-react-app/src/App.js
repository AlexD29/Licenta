import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import Articles from './Articles';
import ArticleDetail from './pages/ArticleDetail';
import Login from './Login';
import Signup from './Signup';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';

function App() {
  const [news, setNews] = useState([]);

  return (
    <BrowserRouter>
        <Navbar />
      <Routes>
        <Route path="/" element={<Articles />} />
        <Route path="/page/:page" element={<Articles />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
