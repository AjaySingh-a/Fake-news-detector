# 📰 Sachify - Fake News Detector

**Sachify** is a machine learning-powered fake news detection web application that helps users verify the authenticity of news articles using Natural Language Processing (NLP) techniques.

---

## 🚀 Features

- ✅ Real-time news text classification (Real or Fake)
- 📄 CSV file upload support for batch testing
- 🧠 ML model powered by TF-IDF and Logistic Regression
- 🌐 Interactive and minimal UI built with Streamlit

---


## 1. Live News Monitoring: View real-time predictions for news articles.![live news](https://github.com/user-attachments/assets/ea0c8701-a4da-4686-9072-442744ca0ef5)
## 2. Check News by Title: Enter a news title to see if it's predicted as real or fake.
![checkbytittle](https://github.com/user-attachments/assets/eef8bca3-7046-44a3-92bb-72d7753669d0)
## 3. News Quiz: Test your fake news detection skills by taking our news quiz.
![quiz](https://github.com/user-attachments/assets/fe8c6ad9-72df-4e9d-bc47-980dd63a84e3)


## Getting Started
- To get started with this project, follow these steps:

  1.Cloning the repository
  
  git clone https://github.com/DJDarkCyber/Fake-News-Detector

  2.Install the required libraries for python

  cd Fake-News-Detector/app/FakeNewsDetectorAPI/ && pip install -r requirements.txt

  3.Install the required libraries for js

  cd ../fake-news-detector-frontend && npm install

  4.Deployment

  Open terminal and cd to project root folder and run

  cd app/FakeNewsDetectorAPI/ && python manage.py migrate && python manage.py runserver

  To load quiz data,

  python manage.py quiz_data_loader game_data/game_data.csv

  Open another terminal and cd to project root folder and run

  cd app/fake-news-detector-frontend/ && npm start

  All set if everything running without errors. Now the deployed web application should open in a browser. If not, open a browser and navigate to http://localhost:3000
