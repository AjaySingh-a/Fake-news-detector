import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Row, Col } from 'react-bootstrap';
import { Check2, X } from 'react-bootstrap-icons';
import { ToastContainer, toast } from 'react-toastify';
import Axios from 'axios';

import Header from './header';

const formatDate = (dateString) => {
  if (!dateString) return 'Date not available';
  try {
    const date = new Date(dateString);
    return isNaN(date) ? 'Invalid date' : 
      `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
  } catch {
    return 'Date format error';
  }
};

const CategoryContainer = () => {
  const { category } = useParams();
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!category) {
      toast.error("Category not specified");
      setLoading(false);
      return;
    }

    const fetchNewsData = async () => {
      try {
        const safeCategory = typeof category === 'string' ? 
          category.charAt(0).toUpperCase() + category.slice(1) : 
          'General';
        
        const response = await Axios.get(`http://127.0.0.1:8000/api/category/${safeCategory}/`);
        setNewsData(Array.isArray(response.data) ? response.data : []);
        
        if (response.data?.length < 10) {
          toast.warning("Limited news available");
        }
      } catch (error) {
        console.error('Error:', error);
        toast.error("Failed to load news");
      } finally {
        setLoading(false);
      }
    };

    fetchNewsData();
  }, [category]);

  if (loading) {
    return (
      <>
        <Header activeContainer={1} />
        <Container className="text-center py-5">
          <p>Loading category news...</p>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header activeContainer={1} />
      <Container className='category-container'>
        {newsData.length > 0 ? (
          <>
            <Row className='main-news-row'>
              {/* Safe rendering for main news item */}
              {newsData[0] && (
                <Col md={8}>
                  <div className="main-news">
                    <h2>{newsData[0]?.title || 'No title available'}</h2>
                    {newsData[0]?.img_url && (
                      <img 
                        src={newsData[0].img_url} 
                        alt="Main news" 
                        className="img-fluid"
                        onError={(e) => {
                          e.target.src = '/fallback-image.jpg';
                        }}
                      />
                    )}
                    <div className="news-meta">
                      <span>{formatDate(newsData[0]?.publication_date)}</span>
                      {newsData[0]?.prediction !== undefined && (
                        <span className={`prediction ${newsData[0].prediction ? 'real' : 'fake'}`}>
                          {newsData[0].prediction ? (
                            <><Check2 /> Real News</>
                          ) : (
                            <><X /> Fake News</>
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                </Col>
              )}
            </Row>

            <Row className="secondary-news">
              {newsData.slice(1).map((news, index) => (
                <Col key={index} md={4} className="mb-4">
                  <div className="news-card">
                    {news?.img_url && (
                      <img
                        src={news.img_url}
                        alt="News thumbnail"
                        className="img-fluid"
                        onError={(e) => {
                          e.target.src = '/fallback-image.jpg';
                        }}
                      />
                    )}
                    <h4>{news?.title || 'Untitled news'}</h4>
                    <div className="news-meta">
                      <span>{formatDate(news?.publication_date)}</span>
                      {news?.prediction !== undefined && (
                        <span className={`prediction ${news.prediction ? 'real' : 'fake'}`}>
                          {news.prediction ? <Check2 /> : <X />}
                        </span>
                      )}
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </>
        ) : (
          <div className="text-center py-5">
            <p>No news available for this category</p>
          </div>
        )}
      </Container>
      <ToastContainer position="bottom-right" />
    </>
  );
};

export default CategoryContainer;