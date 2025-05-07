from rest_framework import serializers
from .models import LiveNews
from django.utils.timezone import localtime
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LiveNewsSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    prediction_display = serializers.SerializerMethodField()
    date_display = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        """Enhanced thumbnail handling with multiple fallbacks"""
        try:
            if obj.img_url and str(obj.img_url).lower() not in ["", "none", "null"]:
                if not obj.img_url.startswith(('http://', 'https://')):
                    return f"https://{obj.img_url}"
                return obj.img_url
                
            # Category-based placeholder images
            category = (obj.news_category or "general").lower()
            placeholders = {
                "sport": "https://via.placeholder.com/300x200/4CAF50/FFFFFF?text=Sports",
                "politics": "https://via.placeholder.com/300x200/2196F3/FFFFFF?text=Politics",
                "technology": "https://via.placeholder.com/300x200/607D8B/FFFFFF?text=Tech",
            }
            return placeholders.get(category, 
                  "https://via.placeholder.com/300x200/9E9E9E/FFFFFF?text=News+Image")
                  
        except Exception as e:
            logger.error(f"Thumbnail error for news {obj.id}: {str(e)}")
            return "https://via.placeholder.com/300x200/FF5722/FFFFFF?text=Image+Error"

    def get_category_display(self, obj):
        """Formatted category name"""
        try:
            if obj.news_category:
                return obj.news_category.replace("_", " ").title()
            return "General News"
        except:
            return "Uncategorized"

    def get_prediction_display(self, obj):
        """Enhanced prediction display with styling"""
        try:
            return {
                True: {"text": "✅ Verified Real", "class": "text-success"},
                False: {"text": "❌ Likely Fake", "class": "text-danger"}
            }.get(obj.prediction, {"text": "⚠️ Unknown", "class": "text-warning"})
        except:
            return {"text": "⚠️ Unknown", "class": "text-warning"}

    def get_date_display(self, obj):
        """Safe date formatting"""
        try:
            if obj.publication_date:
                return localtime(obj.publication_date).strftime("%b %d, %Y")
            return "Date not available"
        except:
            return ""

    def get_time_since(self, obj):
        """Relative time display"""
        try:
            if obj.publication_date:
                delta = datetime.now(localtime(obj.publication_date).tzinfo) - localtime(obj.publication_date)
                
                if delta.days > 365:
                    years = delta.days // 365
                    return f"{years} year{'s' if years > 1 else ''} ago"
                if delta.days > 30:
                    months = delta.days // 30
                    return f"{months} month{'s' if months > 1 else ''} ago"
                if delta.days > 0:
                    return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
                if delta.seconds > 3600:
                    hours = delta.seconds // 3600
                    return f"{hours} hour{'s' if hours > 1 else ''} ago"
                if delta.seconds > 60:
                    minutes = delta.seconds // 60
                    return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                return "Just now"
            return ""
        except Exception as e:
            logger.error(f"Time since error: {str(e)}")
            return ""

    class Meta:
        model = LiveNews
        fields = [
            'id', 'title', 'publication_date', 'date_display', 'time_since',
            'thumbnail', 'news_category', 'category_display',
            'prediction', 'prediction_display', 'section_name',
            'web_url'
        ]
        read_only_fields = fields  # All fields read-only in API

class LiveNewsDetailedSerializer(LiveNewsSerializer):
    section_display = serializers.SerializerMethodField()
    full_date = serializers.SerializerMethodField()
    detailed_prediction = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        """HD version of thumbnail"""
        original = super().get_thumbnail(obj)
        return original.replace("300x200", "800x400") if "placeholder" in original else original

    def get_section_display(self, obj):
        """Formatted section name"""
        try:
            if obj.section_name:
                return obj.section_name.replace("_", " ").title()
            return "General Section"
        except:
            return ""

    def get_full_date(self, obj):
        """Complete date time display"""
        try:
            if obj.publication_date:
                return localtime(obj.publication_date).strftime("%A, %B %d, %Y at %I:%M %p")
            return "Date not available"
        except:
            return ""

    def get_detailed_prediction(self, obj):
        """Prediction with confidence estimation"""
        base = super().get_prediction_display(obj)
        confidence = 95 if obj.prediction else 85  # Example values
        return {
            **base,
            "confidence": confidence,
            "description": "High confidence" if confidence > 90 else "Moderate confidence"
        }

    class Meta:
        model = LiveNews
        fields = '__all__'
        read_only_fields = ['publication_date', 'created_at']