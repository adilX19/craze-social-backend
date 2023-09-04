from django.contrib import admin
from .models import *

@admin.register(InstagramUserProfile)
class InstaProfileAdmin(admin.ModelAdmin):
    list_display = ['django_user', 'insta_userhandle', 'fullName', 'instaId', 'followersCount', 'followCount', 'postsCount']
    search_fields = ['django_user', 'insta_userhandle', 'fullName', 'instaId', 'created']
    list_filter = ['django_user', 'insta_userhandle', 'created']

@admin.register(InstagramProfileInsights)
class InstaInsightsAdmin(admin.ModelAdmin):
    list_display = [
        'insta_userhandle', 'posts_engagement', 'paid_posts_engagement', 
        'reels_engagement', 'posting_growth', 'followers_growth', 'following_growth'
    ]
    search_fields = ['insta_userhandle', 'created']
    list_filter = ['insta_userhandle', 'created']

@admin.register(InstagramProfileHashtag)
class InstaHashtagsAdmin(admin.ModelAdmin):
    list_display = ['hashtag_name', 'item_count', 'created']
    search_fields = ['hashtag_name', 'created']
    list_filter = ['insta_profile', 'created']

