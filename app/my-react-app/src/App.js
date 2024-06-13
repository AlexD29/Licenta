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
import PoliticalParties from './pages/PoliticalParties';
import Cities from './pages/Cities';
import Sources from './pages/Sources';
import Elections from './pages/Elections';
import MyInterests from './pages/MyInterests';
import About from './pages/About';
import PoliticianPage from './entities_pages/PoliticianPage';
import PoliticalPartyPage from './entities_pages/PoliticalPartyPage';
import CityPage from './entities_pages/CityPage';
import SourcePage from './entities_pages/SourcePage';

function App() {
  const userId = 2;

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
          <Route path="/political-parties" element={<PoliticalParties />} />
          <Route path="/cities" element={<Cities />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/alegeri/:category" element={<Elections />} />
          <Route path="/alegeri/:category/page/:page" element={<Elections />} />
          <Route path="/my-interests" element={<MyInterests userId={userId} />} />
          <Route path="/about" element={<About />} />
          <Route path="/politician/:id" element={<PoliticianPage userId={userId} />} />
          <Route path="/politician/:id/page/:page" element={<PoliticianPage userId={userId} />} />
          <Route path="/political-party/:id" element={<PoliticalPartyPage userId={userId} />} />
          <Route path="/political-party/:id/page/:page" element={<PoliticalPartyPage userId={userId} />} />
          <Route path="/city/:id" element={<CityPage userId={userId} />} />
          <Route path="/city/:id/page/:page" element={<CityPage userId={userId} />} />
          <Route path="/source/:id" element={<SourcePage userId={userId} />} />
          <Route path="/source/:id/page/:page" element={<SourcePage userId={userId} />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
