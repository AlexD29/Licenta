import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Elections.css';
import Footer from '../Footer';
import { formatDate } from '../Articles';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { truncateTitle } from '../Articles';
import ElectionChartComponent from 'charts/Home Page/ElectionChartComponent';
import ElectionEmotionsChart from 'charts/Elections/ElectionEmotionsChart';

const formatPastDate = (date) => {
    const options = { day: 'numeric', month: 'long' };
    return date.toLocaleDateString('ro-RO', options);
};

const calculateRemainingDays = (date) => {
    const now = new Date();
    const diffTime = date - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays < 0) {
        return `Alegerile au fost pe ${formatPastDate(date)}`;
    }
    return `${diffDays} zile rămase`;
};

export {calculateRemainingDays, formatPastDate};

const Pagination = ({ currentPage, totalPages, category }) => {
    const renderPagination = (currentPage, totalPages) => {
        let pages = [];
        for (let i = 1; i <= totalPages; i++) {
            pages.push(
                <Link 
                    key={i} 
                    to={`/alegeri/${category}/page/${i}`}
                    className={`pagination-link ${currentPage === i ? 'active' : ''}`}
                >
                    {i}
                </Link>
            );
        }
        return pages;
    };

    return (
        <nav className="pagination gutter-col-xs-0">
            <div className="flex flex-middle">
                <div className="col-3">
                    <Link to={`/alegeri/${category}/page/${currentPage > 1 ? currentPage - 1 : 1}`} className="pagination-link pagination-link-prev" rel="prev">
                        <svg width="100%" height="100%" viewBox="0 0 16 16" version="1.1" style={{ fillRule: 'evenodd', clipRule: 'evenodd', strokeLinejoin: 'round', strokeMiterlimit: 2 }}>
                            <g id="Icon">
                                <path d="M11.53,13.47l-5.469,-5.47c-0,-0 5.469,-5.47 5.469,-5.47c0.293,-0.292 0.293,-0.768 0,-1.06c-0.292,-0.293 -0.768,-0.293 -1.06,-0l-6,6c-0.293,0.293 -0.293,0.767 -0,1.06l6,6c0.292,0.293 0.768,0.293 1.06,0c0.293,-0.292 0.293,-0.768 0,-1.06Z"></path>
                            </g>
                        </svg>
                    </Link>
                </div>
                <span className="current-page">{currentPage}</span>
                <div className="col-3 col-end">
                    <Link to={`/alegeri/${category}/page/${currentPage < totalPages ? currentPage + 1 : totalPages}`} className="pagination-link pagination-link-next">
                        <svg version="1.1" id="Layer_1" x="0px" y="0px" viewBox="0 0 32 32" style={{ enableBackground: 'new 0 0 32 32' }}>
                            <g>
                                <path d="M11.5,26c-0.3,0-0.5-0.1-0.7-0.3c-0.4-0.4-0.4-1,0-1.4l8.3-8.3l-8.3-8.3c-0.4-0.4-0.4-1,0-1.4s1-0.4,1.4,0l9,9
                                c0.4,0.4,0.4,1,0,1.4l-9,9C12,25.9,11.8,26,11.5,26z"></path>
                            </g>
                        </svg>
                    </Link>
                </div>
            </div>
        </nav>
    );
};

const Elections = () => {
    const { category } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [articles, setArticles] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedCategory, setSelectedCategory] = useState(category || 'toate-alegerile');

    const getApiUrl = (category) => {
        switch (category) {
            case 'alegeri-locale':
                return 'http://localhost:8000/api/alegeri/Alegeri%20Locale';
            case 'alegeri-europarlamentare':
                return 'http://localhost:8000/api/alegeri/Alegeri%20Europarlamentare';
            case 'alegeri-prezidentiale':
                return 'http://localhost:8000/api/alegeri/Alegeri%20Prezidențiale';
            case 'alegeri-parlamentare':
                return 'http://localhost:8000/api/alegeri/Alegeri%20Parlamentare';
            default:
                return 'http://localhost:8000/api/alegeri/Toate%20Alegerile';
        }
    };    

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const apiUrl = getApiUrl(category);
                const response = await axios.get(`${apiUrl}?page=${currentPage}&limit=10`);
                setData(response.data);
                setArticles(response.data.articles);
                setTotalPages(response.data.totalPages);
                setCurrentPage(1);
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [category, currentPage]);

    const handleClick = (newCategory) => {
        setCurrentPage(1);
        setSelectedCategory(newCategory);
        navigate(`/alegeri/${newCategory}`);
    };

    const electionDates = {
        'Alegeri Europarlamentare': new Date('2024-06-09'),
        'Alegeri Locale': new Date('2024-06-09'),
        'Alegeri Prezidențiale': new Date('2024-09-15'),
        'Alegeri Parlamentare': new Date('2024-12-08')
    };


    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-animation"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!data) {
        return <div>Niciun rezultat.</div>;
    }

    return (
        <div className='alegeri-container'>
            <div className='alegeri-message-div'>
                <span className='alegeri-message'>Votul tău contează!</span>
            </div>
            <div className='alegeri-content'>
                <div className='first-part not-enough'>
                    <ul className='alegeri-list'>
                        <Link to='/alegeri/toate-alegerile' className='alegeri-link'>
                        <li 
                                className={`alegeri-list-item ${selectedCategory === 'toate-alegerile' ? 'selected' : ''}`} 
                                onClick={() => handleClick('toate-alegerile')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/toate_alegerile.png`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Toate Alegerile</p>
                                </div>
                            </li>
                        </Link>
                        <Link to='/alegeri/alegeri-locale' className='alegeri-link'>
                            <li 
                                className={`alegeri-list-item ${selectedCategory === 'alegeri-locale' ? 'selected' : ''}`} 
                                onClick={() => handleClick('alegeri-locale')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/alegeri-locale.jpg`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Alegeri Locale</p>
                                    <p>{calculateRemainingDays(electionDates['Alegeri Locale'])}</p>
                                </div>
                            </li>
                        </Link>
                        <Link to='/alegeri/alegeri-europarlamentare' className='alegeri-link'>
                            <li 
                                className={`alegeri-list-item ${selectedCategory === 'alegeri-europarlamentare' ? 'selected' : ''}`} 
                                onClick={() => handleClick('alegeri-europarlamentare')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/alegeri-europarlamentare.jpg`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Alegeri Europarlamentare</p>
                                    <p>{calculateRemainingDays(electionDates['Alegeri Europarlamentare'])}</p>
                                </div>
                            </li>
                        </Link>
                        <Link to='/alegeri/alegeri-prezidentiale' className='alegeri-link'>
                            <li 
                                className={`alegeri-list-item ${selectedCategory === 'alegeri-prezidentiale' ? 'selected' : ''}`} 
                                onClick={() => handleClick('alegeri-prezidentiale')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/alegeri-prezidentiale.jpg`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Alegeri Prezidențiale</p>
                                    <p>{calculateRemainingDays(electionDates['Alegeri Prezidențiale'])}</p>
                                </div>
                            </li>
                        </Link>
                        <Link to='/alegeri/alegeri-parlamentare' className='alegeri-link'>
                            <li 
                                className={`alegeri-list-item ${selectedCategory === 'alegeri-parlamentare' ? 'selected' : ''}`} 
                                onClick={() => handleClick('alegeri-parlamentare')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/alegeri-parlamentare.jpg`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Alegeri Parlamentare</p>
                                    <p>{calculateRemainingDays(electionDates['Alegeri Parlamentare'])}</p>
                                </div>
                            </li>
                        </Link>
                    </ul>
                    <ElectionEmotionsChart category={category} />
                </div>
                <div className="second-part">
                    <div className="articles-part">
                        {articles.map((article) => (
                        <Link
                            key={article.id}
                            to={`/article/${article.id}`}
                            className="article-link-minimized"
                        >
                            <div
                            className={`article-card-minimized ${article.emotion.toLowerCase()}`}
                            >
                            <div className="article-image-div-minimized">
                                <img
                                src={article.image_url}
                                className="article-image-minimized"
                                alt=""
                                />
                            </div>
                            <div className="article-details-div-minimized">
                                <h3 className="article-text-minimized">
                                {truncateTitle(article.title, 130)}
                                </h3>
                                <div className="article-date-and-source">
                                <p className="article-text-minimized">
                                    {formatDate(article.published_date)}
                                </p>
                                <div className="article-source-image-minimized">
                                    <img
                                    src={article.source_image_url}
                                    alt={article.source_name}
                                    className="source-icon-minimized"
                                    />
                                </div>
                                </div>
                            </div>
                            </div>
                        </Link>
                        ))}
                    </div>
                    <Pagination currentPage={currentPage} totalPages={totalPages} category={category} />
                </div>
                <div className='third-part'>
                    <ElectionChartComponent startDate="2024-01-01" />
                </div>
            </div>
            <Footer/>
        </div>
    );
};

export default Elections;
