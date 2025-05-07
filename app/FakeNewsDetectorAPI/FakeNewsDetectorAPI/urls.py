from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from core.livenews.viewsets import (
    LiveNewsPrediction,
    LiveNewsByCategory,
    TitleCheckViewSet
)
from core.usercheckbytitle.viewsets import UserCheckViewSet
from core.newsquiz.viewsets import NewsQuizViewSet

# Register all routers
router = DefaultRouter()
router.register(r'news', LiveNewsPrediction, basename='live-news')
router.register(r'usercheck/title', UserCheckViewSet, basename='user-title-check')
router.register(r'quiz', NewsQuizViewSet, basename='quiz')

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Main API endpoints via router
    path('api/', include(router.urls)),

    # Category-based filtering
    re_path(
        r'^api/category/(?P<category>[a-zA-Z0-9\s-]+)/$',
        LiveNewsByCategory.as_view({'get': 'list'}),
        name='news-by-category'
    ),

    # Title verification endpoint
    path(
        'api/verify-title/',
        TitleCheckViewSet.as_view({'post': 'create'}),
        name='verify-title'
    ),

    # Browsable API login
    path('api-auth/', include('rest_framework.urls')),

    # Optional: API documentation
    path('api/docs/', include_docs_urls(title='News Verification API')),
]
