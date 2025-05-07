from rest_framework.response import Response
from rest_framework import viewsets, status
import requests
from bs4 import BeautifulSoup
from .models import LiveNews
from .serializers import LiveNewsDetailedSerializer
from core.model import load_models
import threading
import time
from django.core.cache import cache
from django.db.models import Q
from fake_useragent import UserAgent
import json

ua = UserAgent()

def scrap_img_from_web(url):
    try:
        headers = {'User-Agent': ua.random}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            return None
            
        soup = BeautifulSoup(r.content, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
            
        schema_image = soup.find('img', itemprop='image')
        if schema_image and schema_image.get('src'):
            return schema_image['src']
            
        content_image = soup.find('article').find('img') if soup.find('article') else None
        if content_image and content_image.get('src'):
            return content_image['src']
            
        return None
    except Exception as e:
        print(f"Image scraping error for {url}: {str(e)}")
        return None

def get_new_news_from_api_and_update():
    try:
        # Priority 1: Direct sports news fetch
        sports_response = requests.get(
            "https://content.guardianapis.com/sport?api-key=e705adff-ca49-414e-89e2-7edede919e2e&show-fields=thumbnail&page-size=20",
            timeout=15
        )
        sports_data = sports_response.json()

        # Priority 2: General news fallback
        general_response = requests.get(
            "https://content.guardianapis.com/search?api-key=e705adff-ca49-414e-89e2-7edede919e2e&show-fields=thumbnail&page-size=10",
            timeout=15
        )
        general_data = general_response.json()

        nb_model, vect_model = load_models()

        # Process sports news first
        if sports_data.get('response', {}).get('results'):
            for article in sports_data['response']['results']:
                web_url = article["webUrl"]
                img_url = article.get("fields", {}).get("thumbnail")
                
                if not img_url or img_url == "None":
                    img_url = scrap_img_from_web(web_url)
                
                LiveNews.objects.update_or_create(
                    web_url=web_url,
                    defaults={
                        'title': article["webTitle"],
                        'publication_date': article["webPublicationDate"],
                        'news_category': 'Sports',
                        'prediction': nb_model.predict(vect_model.transform([article["webTitle"]]))[0] == 1,
                        'section_id': article["sectionId"],
                        'section_name': article["sectionName"],
                        'type': article["type"],
                        'img_url': img_url if img_url else "None",
                        'is_sports': True
                    }
                )

        # Process general news
        if general_data.get('response', {}).get('results'):
            for article in general_data['response']['results']:
                web_url = article["webUrl"]
                img_url = article.get("fields", {}).get("thumbnail")
                
                if not img_url or img_url == "None":
                    img_url = scrap_img_from_web(web_url)
                
                LiveNews.objects.update_or_create(
                    web_url=web_url,
                    defaults={
                        'title': article["webTitle"],
                        'publication_date': article["webPublicationDate"],
                        'news_category': article.get("sectionName", "General"),
                        'prediction': nb_model.predict(vect_model.transform([article["webTitle"]]))[0] == 1,
                        'section_id': article["sectionId"],
                        'section_name': article["sectionName"],
                        'type': article["type"],
                        'img_url': img_url if img_url else "None",
                        'is_sports': False
                    }
                )

    except Exception as e:
        print(f"Error in news update: {str(e)}")

class LiveNewsPrediction(viewsets.ViewSet):
    http_method_names = ['get']

    def list(self, request):
        cache_key = 'all_live_news'
        data = cache.get(cache_key)
        
        if not data:
            all_live_news = LiveNews.objects.all().order_by('-publication_date')[:20]
            serializer = LiveNewsDetailedSerializer(all_live_news, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=300)
        
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            news_item = LiveNews.objects.get(pk=pk)
            serializer = LiveNewsDetailedSerializer(news_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LiveNews.DoesNotExist:
            return Response(
                {"error": "News item not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class LiveNewsByCategory(viewsets.ViewSet):
    def list(self, request, category=None):
        category = category.lower().strip()
        cache_key = f'news_category_{category}'
        data = cache.get(cache_key)
        
        if not data:
            sports_keywords = ['sports', 'sport', 'football', 'cricket']
            
            if category in sports_keywords:
                live_news = LiveNews.objects.filter(
                    Q(news_category__icontains='sport') |
                    Q(section_name__icontains='sport') |
                    Q(title__icontains='sport')
                ).order_by('-publication_date')[:15]
            else:
                live_news = LiveNews.objects.filter(
                    Q(news_category__icontains=category) |
                    Q(section_name__icontains=category) |
                    Q(title__icontains=category)
                ).order_by('-publication_date')[:10]
            
            if not live_news.exists():
                return Response(
                    {"message": f"No news found for category: {category}"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            serializer = LiveNewsDetailedSerializer(live_news, many=True)
            data = serializer.data
            cache.set(cache_key, data, timeout=300)
        
        return Response(data, status=status.HTTP_200_OK)

class TitleCheckViewSet(viewsets.ViewSet):
    def create(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            
            if len(title) < 10:
                return Response(
                    {"error": "Title must be at least 10 characters long"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            nb_model, vect_model = load_models()
            vec_title = vect_model.transform([title])
            prediction = nb_model.predict(vec_title)[0]
            confidence = max(nb_model.predict_proba(vec_title)[0]) * 100
            
            return Response({
                "title": title,
                "prediction": "Real" if prediction == 1 else "Fake",
                "confidence": round(float(confidence), 2),
                "status": "success"
            })
        except Exception as e:
            return Response(
                {"error": f"Prediction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def auto_refresh_news():
    while True:
        try:
            print("Starting news refresh...")
            nb_model, vectorizer = load_models()
            get_new_news_from_api_and_update()
            print("News refresh completed successfully")
            time.sleep(600)
        except Exception as e:
            print(f"Auto-refresh error: {str(e)}")
            time.sleep(60)

auto_refresh_thread = threading.Thread(target=auto_refresh_news)
auto_refresh_thread.daemon = True
auto_refresh_thread.start()