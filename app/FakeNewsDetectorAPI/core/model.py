import pickle
import os
import logging
from django.conf import settings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.exceptions import NotFittedError

# Set up logging
logger = logging.getLogger(__name__)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'models')

def load_models():
    """Enhanced model loading with comprehensive error handling"""
    try:
        # Verify model directory exists
        if not os.path.exists(MODEL_PATH):
            logger.warning("Models directory not found, creating new models")
            return create_and_save_models()

        # Load Naive Bayes model
        nb_path = os.path.join(MODEL_PATH, 'nb_model.pkl')
        if not os.path.exists(nb_path):
            logger.error("Naive Bayes model file not found")
            raise FileNotFoundError("nb_model.pkl not found")
            
        with open(nb_path, 'rb') as f:
            nb_model = pickle.load(f)
            if not isinstance(nb_model, MultinomialNB):
                raise ValueError("Invalid model type loaded")

        # Load Vectorizer
        vec_path = os.path.join(MODEL_PATH, 'vectorizer_model.pkl')
        if not os.path.exists(vec_path):
            logger.error("Vectorizer model file not found")
            raise FileNotFoundError("vectorizer_model.pkl not found")
            
        with open(vec_path, 'rb') as f:
            vectorizer = pickle.load(f)
            if not isinstance(vectorizer, CountVectorizer):
                raise ValueError("Invalid vectorizer type loaded")
            
            # Verify vectorizer is properly fitted
            try:
                vectorizer.transform(["test input"])
            except NotFittedError:
                logger.error("Vectorizer not properly fitted")
                raise

        return nb_model, vectorizer

    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
        return create_and_save_models()  # Fallback to creating new models

def create_and_save_models():
    """Create and save new models with better initialization"""
    logger.info("Creating new models...")
    try:
        # Initialize with better parameters
        vectorizer = CountVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        nb_model = MultinomialNB(alpha=0.1)
        
        # Improved dummy training data
        dummy_texts = [
            "This is a legitimate news article about current events",
            "Fake news story spreading misinformation",
            "Verified report from trusted journalist",
            "False claims going viral on social media"
        ]
        dummy_labels = [1, 0, 1, 0]  # 1=real, 0=fake
        
        # Fit models
        X = vectorizer.fit_transform(dummy_texts)
        nb_model.fit(X, dummy_labels)
        
        # Save models
        save_models(nb_model, vectorizer)
        return nb_model, vectorizer
        
    except Exception as e:
        logger.critical(f"Model creation failed: {str(e)}")
        raise

def save_models(nb_model, vectorizer):
    """Safe model saving with directory creation"""
    try:
        os.makedirs(MODEL_PATH, exist_ok=True)
        
        # Save with protocol version for compatibility
        with open(os.path.join(MODEL_PATH, 'nb_model.pkl'), 'wb') as f:
            pickle.dump(nb_model, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        with open(os.path.join(MODEL_PATH, 'vectorizer_model.pkl'), 'wb') as f:
            pickle.dump(vectorizer, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        logger.info("Models successfully saved")
        
    except Exception as e:
        logger.error(f"Failed to save models: {str(e)}")
        raise