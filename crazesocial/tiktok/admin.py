from django.contrib import admin
from .models import *

@admin.register(TiktokUserProfile)
class TiktokProfileAdmin(admin.ModelAdmin):
    list_display = ['django_user', 'tiktok_userhandle', 'fullName', 'user_id', 'followers', 'followings', 'videos_count', 'likes']
    search_fields = ['django_user', 'tiktok_userhandle', 'fullName', 'user_id', 'created']
    list_filter = ['django_user', 'tiktok_userhandle', 'created']

@admin.register(TiktokProfileInsights)
class TiktokInsightsAdmin(admin.ModelAdmin):
    list_display = [
        'tiktok_userhandle', 'posts_engagement', 'paid_posts_engagement', 'posting_growth', 'followers_growth', 'following_growth'
    ]
    search_fields = ['tiktok_userhandle', 'created']
    list_filter = ['tiktok_userhandle', 'created']

@admin.register(TiktokProfileHashtag)
class TiktokHashtagsAdmin(admin.ModelAdmin):
    list_display = ['hashtag_name', 'item_count', 'created']
    search_fields = ['hashtag_name', 'created']
    list_filter = ['tiktok_profile', 'created']