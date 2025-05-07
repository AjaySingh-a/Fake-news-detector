import React, { useState, useEffect } from 'react';
import Header from './header';
import Axios from 'axios';
import { Container, Button, Spinner } from 'react-bootstrap';
import { ToastContainer, toast } from 'react-toastify';

function NewsQuiz() {
  document.title = 'SACHIFY | News Quiz';
  const stage = 3;
  const [quizData, setQuizData] = useState({
    news_title: '',
    news_description: '',
    label: null,
    loading: true,
    error: null
  });
  const [selectedAnswer, setSelectedAnswer] = useState('');

  useEffect(() => {
    fetchQuizData();
  }, []);

  const fetchQuizData = async () => {
    try {
      setQuizData(prev => ({ ...prev, loading: true, error: null }));
      const response = await Axios.get('http://127.0.0.1:8000/api/quiz/');
      
      if (response.data) {
        setQuizData({
          news_title: response.data.news_title || '',
          news_description: response.data.news_description || '',
          label: response.data.label,
          loading: false,
          error: null
        });
      }
    } catch (error) {
      console.error('Error fetching quiz:', error);
      setQuizData(prev => ({
        ...prev,
        loading: false,
        error: 'Failed to load quiz'
      }));
      toast.error('Failed to load quiz. Please try again.');
    }
  };

  const handleOptionChange = (e) => {
    setSelectedAnswer(e.target.value);
  };

  const checkAnswer = () => {
    if (!selectedAnswer) {
      toast.error('Please select an answer!');
      return;
    }

    if (
      (quizData.label === true && selectedAnswer === 'True') ||
      (quizData.label === false && selectedAnswer === 'False')
    ) {
      toast.success("Correct prediction!");
    } else {
      toast.warning("Incorrect prediction");
    }
  };

  const getNewQuiz = () => {
    setSelectedAnswer('');
    fetchQuizData();
  };

  if (quizData.loading) {
    return (
      <>
        <Header activeContainer={stage} />
        <Container className='news-quiz-container text-center py-5'>
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </Container>
      </>
    );
  }

  if (quizData.error) {
    return (
      <>
        <Header activeContainer={stage} />
        <Container className='news-quiz-container text-center py-5'>
          <p className="text-danger">{quizData.error}</p>
          <Button onClick={fetchQuizData} variant="primary">
            Retry
          </Button>
        </Container>
      </>
    );
  }

  return (
    <>
      <Header activeContainer={stage} />
      <Container className='news-quiz-container'>
        <div className='div-iqyla'>
          <h4>{quizData.news_title}</h4>
        </div>
        <div className='div-iqpls'>
          <p>{quizData.news_description}</p>
        </div>

        <div className="radiogroup">
          <div className='div-oqapl'>
            <div className='div-ioalp'>
              <div className="wrapper">
                <input
                  className="state"
                  type="radio"
                  value="True"
                  name="quizAnswer"
                  id="quizTrue"
                  checked={selectedAnswer === 'True'}
                  onChange={handleOptionChange}
                />
                <label className="label" htmlFor="quizTrue">
                  <div className="indicator"></div>
                  <span className="text">Real News</span>
                </label>
              </div>
              <div className="wrapper">
                <input
                  className="state"
                  type="radio"
                  value="False"
                  name="quizAnswer"
                  id="quizFalse"
                  checked={selectedAnswer === 'False'}
                  onChange={handleOptionChange}
                />
                <label className="label" htmlFor="quizFalse">
                  <div className="indicator"></div>
                  <span className="text">Fake News</span>
                </label>
              </div>
            </div>
            <div className='div-oapql'>
              <Button
                variant="primary"
                onClick={checkAnswer}
                className='button-17'
                disabled={!selectedAnswer}
              >
                Submit
              </Button>
              <Button
                onClick={getNewQuiz}
                variant="light"
                className='button-17 ms-2'
              >
                New Quiz
              </Button>
            </div>
          </div>
        </div>
      </Container>
      <ToastContainer position="bottom-right" autoClose={3000} />
    </>
  );
}

export default NewsQuiz;