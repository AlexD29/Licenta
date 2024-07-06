import React, { useEffect, useState } from 'react';
import axios from 'axios';
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
import SearchResults from './SearchResults';

function App() {
  const [userId, setUserId] = useState(null);
  const [email, setEmail] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/protected', {
          withCredentials: true, // Include credentials (cookies)
        });
        const data = response.data;
        if (response.status === 200 && data.user) {
          setUserId(data.user.id);
          setEmail(data.user.email);
        } else {
          console.log(data.message);
        }
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, []);

  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar email={email} />
        <Routes>
          <Route path="/" element={<Articles userId={userId}/>} />
          <Route path="/page/:page" element={<Articles userId={userId}/>} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/politicians" element={<Politicians userId={userId} />} />
          <Route path="/political-parties" element={<PoliticalParties userId={userId} />} />
          <Route path="/cities" element={<Cities userId={userId} />} />
          <Route path="/sources" element={<Sources />} />
          <Route path="/alegeri/:category" element={<Elections />} />
          <Route path="/alegeri/:category/page/:page" element={<Elections />} />
          <Route path="/my-interests" element={<MyInterests userId={userId} />} />
          <Route path="/politician/:id" element={<PoliticianPage userId={userId} />} />
          <Route path="/politician/:id/page/:page" element={<PoliticianPage userId={userId} />} />
          <Route path="/political-party/:id" element={<PoliticalPartyPage userId={userId} />} />
          <Route path="/political-party/:id/page/:page" element={<PoliticalPartyPage userId={userId} />} />
          <Route path="/city/:id" element={<CityPage userId={userId} />} />
          <Route path="/city/:id/page/:page" element={<CityPage userId={userId} />} />
          <Route path="/source/:id" element={<SourcePage userId={userId} />} />
          <Route path="/source/:id/page/:page" element={<SourcePage userId={userId} />} />
          <Route path="/search" element={<SearchResults userId={userId} />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
