import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Header from './header';
import { Container, Form, Button } from 'react-bootstrap';
import Axios from 'axios';
import { Check2, X } from 'react-bootstrap-icons';

function CheckByTitle() {
  document.title = 'Sachify | Check news by title';
  const stage = 2;
  const [inputNewsTitle, setNewsTitle] = useState('');
  const [predictedValue, setPredictedValue] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!inputNewsTitle?.trim()) {
      toast.error('Please enter some text!');
      return;
    }

    setIsLoading(true);

    Axios.post('http://127.0.0.1:8000/api/usercheck/title/', {
      user_news: inputNewsTitle
    })
      .then((response) => {
        const prediction = response.data?.prediction;
        if (typeof prediction === 'boolean') {
          const result = prediction ? 'True' : 'False';
          setPredictedValue(result);
          toast[result === 'True' ? 'success' : 'error'](
            result === 'True' ? "Real news!" : "Fake news!",
            result === 'False' ? { icon: <X style={{ color: 'white', backgroundColor: 'red' }} /> } : undefined
          );
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        toast.error('Error checking news. Please try again.');
        setPredictedValue(null);
      })
      .finally(() => setIsLoading(false));
  };

  return (
    <>
      <Header activeContainer={stage} />
      <Container fluid="lg" className="check-by-title-container">
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label className='frm-opalq'>News Title</Form.Label>
            <Form.Control
              className='frm-moqpa'
              as="textarea"
              rows={5}
              placeholder="Enter news title..."
              value={inputNewsTitle}
              onChange={(e) => setNewsTitle(e.target.value)}
            />
          </Form.Group>
          <Button
            variant="primary"
            type="submit"
            className='button-17'
            disabled={isLoading || !inputNewsTitle?.trim()}
          >
            {isLoading ? 'Checking...' : 'Check'}
          </Button>
        </Form>
      </Container>

      {predictedValue && (
        <Container className='prediction-result-container'>
          {predictedValue === 'True' ? (
            <div className='true'>
              <div><Check2 className='true-news-icon' /></div>
              Predicted as real news!
            </div>
          ) : (
            <div className='false'>
              <div><X className='fake-news-icon' /></div>
              Predicted as fake news!
            </div>
          )}
        </Container>
      )}
      
      <ToastContainer position="bottom-right" autoClose={5000} />
    </>
  );
}

export default CheckByTitle;