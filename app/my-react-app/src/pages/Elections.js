import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Elections.css';
import Footer from '../Footer';
import { formatDate } from '../Articles';
import { Link, useParams, useNavigate } from 'react-router-dom';

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
                    <Link to={`/alegeri/${category}/page/1`} className="pagination-link pagination-link-prev">
                        <svg version="1.1" id="Layer_1" x="0px" y="0px" width="92px" height="92px" viewBox="0 0 92 92" enableBackground="new 0 0 92 92">
                            <path id="XMLID_646_" d="M78.7,9.4c-1.4-0.7-3-0.5-4.2,0.5L33,42.9c-1,0.8-1.5,1.9-1.5,3.1s0.6,2.4,1.5,3.1l41.5,33
                            c0.7,0.6,1.6,0.9,2.5,0.9c0.6,0,1.2-0.1,1.7-0.4c1.4-0.7,2.3-2.1,2.3-3.6V13C81,11.5,80.1,10.1,78.7,9.4z M73,70.7L41.9,46L73,21.3
                            V70.7z M19,14.6v63.5c0,2.5-2,4.5-4.5,4.5s-4.5-2-4.5-4.5V14.6c0-2.5,2-4.5,4.5-4.5S19,12.1,19,14.6z"></path>
                        </svg>
                    </Link>
                    <Link to={`/alegeri/${category}/page/${currentPage > 1 ? currentPage - 1 : 1}`} className="pagination-link pagination-link-prev" rel="prev">
                        <svg width="100%" height="100%" viewBox="0 0 16 16" version="1.1" style={{ fillRule: 'evenodd', clipRule: 'evenodd', strokeLinejoin: 'round', strokeMiterlimit: 2 }}>
                            <g id="Icon">
                                <path d="M11.53,13.47l-5.469,-5.47c-0,-0 5.469,-5.47 5.469,-5.47c0.293,-0.292 0.293,-0.768 0,-1.06c-0.292,-0.293 -0.768,-0.293 -1.06,-0l-6,6c-0.293,0.293 -0.293,0.767 -0,1.06l6,6c0.292,0.293 0.768,0.293 1.06,0c0.293,-0.292 0.293,-0.768 0,-1.06Z"></path>
                            </g>
                        </svg>
                    </Link>
                </div>
                <div className="col-6 col-center">
                    {renderPagination(currentPage, totalPages)}
                </div>
                <div className="col-3 col-end">
                    <Link to={`/alegeri/${category}/page/${currentPage < totalPages ? currentPage + 1 : totalPages}`} className="pagination-link pagination-link-next">
                        <svg version="1.1" id="Layer_1" x="0px" y="0px" viewBox="0 0 32 32" style={{ enableBackground: 'new 0 0 32 32' }}>
                            <g>
                                <path d="M11.5,26c-0.3,0-0.5-0.1-0.7-0.3c-0.4-0.4-0.4-1,0-1.4l8.3-8.3l-8.3-8.3c-0.4-0.4-0.4-1,0-1.4s1-0.4,1.4,0l9,9
                                c0.4,0.4,0.4,1,0,1.4l-9,9C12,25.9,11.8,26,11.5,26z"></path>
                            </g>
                        </svg>
                    </Link>
                    <Link to={`/alegeri/${category}/page/${totalPages}`} className="pagination-link pagination-link-next" rel="next">
                        <svg version="1.1" id="Layer_1" x="0px" y="0px" width="92px" height="92px" viewBox="0 0 92 92" enableBackground="new 0 0 92 92" xmlSpace="preserve">
                            <path id="XMLID_659_" d="M59.5,42.9l-42-33c-1.2-0.9-2.8-1.1-4.2-0.5C11.9,10.1,11,11.5,11,13v66c0,1.5,0.9,2.9,2.3,3.6
                            c0.6,0.3,1.2,0.4,1.7,0.4c0.9,0,1.8-0.3,2.5-0.9l42-33c1-0.8,1.5-1.9,1.5-3.1C61,44.8,60.4,43.6,59.5,42.9z M19,70.8V21.2L50.5,46
                            L19,70.8z M81,14.6v63.5c0,2.5-2,4.5-4.5,4.5s-4.5-2-4.5-4.5V14.6c0-2.5,2-4.5,4.5-4.5S81,12.1,81,14.6z"></path>
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

    const calculateRemainingDays = (date) => {
        const now = new Date();
        const diffTime = Math.abs(date - now);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays;
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
                <div className='first-part'>
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
                                    <p>{calculateRemainingDays(electionDates['Alegeri Locale'])} zile rămase</p>
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
                                    <p>{calculateRemainingDays(electionDates['Alegeri Europarlamentare'])} zile rămase</p>
                                </div>
                            </li>
                        </Link>
                        <Link to='/alegeri/alegeri-prezidentiale' className='alegeri-link'>
                            <li 
                                className={`alegeri-list-item ${selectedCategory === 'alegeri-prezidentiale' ? 'selected' : ''}`} 
                                onClick={() => handleClick('alegeri-prezidentiale')}
                            >
                                <img src={`${process.env.PUBLIC_URL}/explore/alegeri-prezidențiale.jpg`} alt="Image" className="alegeri-list-image" />
                                <div className="alegeri-list-text">
                                    <p>Alegeri Prezidențiale</p>
                                    <p>{calculateRemainingDays(electionDates['Alegeri Prezidențiale'])} zile rămase</p>
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
                                    <p>{calculateRemainingDays(electionDates['Alegeri Parlamentare'])} zile rămase</p>
                                </div>
                            </li>
                        </Link>
                    </ul>
                </div>
                <div className='second-part'>
                    <div className='articles-part'>
                    {articles.map((article) => (
                        <Link key={article.id} to={`/article/${article.id}`} className="article-link-minimized">
                            <div className={`article-card-minimized ${article.emotion.toLowerCase()}`}>
                                <div className="article-image-div-minimized">
                                    <img src={article.image_url} className="article-image-minimized" />
                                </div>
                                <div className="article-details-div-minimized">
                                    <h3 className="article-text-minimized">{article.title}</h3>
                                    <p className="article-text-minimized">{formatDate(article.published_date)}</p>
                                </div>
                                <div className="article-source-image-minimized">
                                    <img src={article.source_image_url} alt={article.source_name} className="source-icon-minimized" />
                                </div>
                            </div>
                        </Link>
                    ))}
                    </div>
                    <Pagination currentPage={currentPage} totalPages={totalPages} category={category} />
                </div>
            </div>
            <Footer/>
        </div>
    );
};

export default Elections;
