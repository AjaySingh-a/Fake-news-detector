import React, { useEffect, useState, useCallback } from 'react';
import { Container, Spinner, Alert } from 'react-bootstrap';
import { Check2, X, Trophy } from 'react-bootstrap-icons';
import { ToastContainer, toast } from 'react-toastify';
import Axios from 'axios';
import Header from './header';

const Home = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSports, setIsSports] = useState(false);
  const [error, setError] = useState(null);

  const fetchNews = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try sports endpoints first
      const sportsEndpoints = [
        '/api/category/sports/',
        '/api/category/sport/',
        '/api/category/football/'
      ];

      for (const endpoint of sportsEndpoints) {
        try {
          const response = await Axios.get(`http://127.0.0.1:8000${endpoint}`);
          if (response.data?.length > 0) {
            setNews(response.data);
            setIsSports(true);
            setLoading(false);
            return;
          }
        } catch (e) {
          console.log(`Sports endpoint ${endpoint} failed:`, e.message);
        }
      }

      // Fallback to featured news
      const featuredResponse = await Axios.get('http://127.0.0.1:8000/api/featured/');
      setNews(featuredResponse.data || []);
      setIsSports(false);
      
    } catch (err) {
      console.error('News fetch error:', err);
      setError('Failed to load news. Please try again later.');
      try {
        const cachedResponse = await Axios.get('http://127.0.0.1:8000/api/news/');
        setNews(cachedResponse.data || []);
      } catch (cacheErr) {
        console.error('Cache fallback failed:', cacheErr);
        setNews([]);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  if (loading) {
    return (
      <>
        <Header activeContainer={1} />
        <Container className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">Loading latest sports news...</p>
        </Container>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Header activeContainer={1} />
        <Container className="py-4">
          <Alert variant="danger">{error}</Alert>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header activeContainer={1} />
      <Container className="home-container">
        <div className="category-header">
          {isSports ? (
            <>
              <Trophy className="me-2" color="gold" size={24} />
              <h2>Sports News</h2>
            </>
          ) : (
            <h2>Featured News</h2>
          )}
        </div>

        {news.length === 0 ? (
          <div className="text-center py-5">
            <p>No news available right now. Please check back later.</p>
          </div>
        ) : (
          <div className="news-grid">
            {news.map((item, index) => (
              <div key={`${item.id}-${index}`} className="news-card">
                {item.img_url && item.img_url !== "None" && (
                  <img 
                    src={item.img_url} 
                    alt={item.title} 
                    className="news-image"
                    onError={(e) => e.target.style.display = 'none'}
                  />
                )}
                <div className="news-content">
                  <h3>{item.title || 'Untitled News'}</h3>
                  <p className="news-desc">
                    {item.description || 'No description available'}
                  </p>
                  <div className={`news-verdict ${item.prediction ? 'real' : 'fake'}`}>
                    {item.prediction ? (
                      <>
                        <Check2 /> Verified Real
                      </>
                    ) : (
                      <>
                        <X /> Potential Fake
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Container>
      <ToastContainer position="bottom-right" />
    </>
  );
};

export default Home;