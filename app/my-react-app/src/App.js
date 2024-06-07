import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import Navbar from './Navbar';
import Articles from './Articles';
import ArticleDetail from './pages/ArticleDetail';
import Login from './Login';
import Signup from './Signup';
import Explore from './pages/Explore';
import './App.css';
import Politicians from './pages/Politicians';
import Political_parties from './pages/Political-parties';
import Cities from './pages/Cities';
import Elections from './pages/Elections';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <Routes>
          <Route path="/" element={<Articles />} />
          <Route path="/page/:page" element={<Articles />} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/politicians" element={<Politicians />} />
          <Route path="/political-parties" element={<Political_parties />} />
          <Route path="/cities" element={<Cities />} />
          <Route path="/alegeri/:category" element={<Elections />} />
          <Route path="/alegeri/:category/page/:page" element={<Elections />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
