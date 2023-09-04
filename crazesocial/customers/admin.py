from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'gender']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['django_user', 'tiktok_user_handle', 'insta_user_handle']
    search_display = ['django_user', 'tiktok_user_handle', 'insta_user_handle']


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ['customer', 'tiktok_user_handle', 'insta_user_handle']
    search_display = ['customer', 'tiktok_user_handle', 'insta_user_handle']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['django_user', 'customer_handle', 'competitors', 'common_profiles', 'flow_name', 'status',
                    'created']
    search_display = ['django_user', 'customer_handle', 'competitors', 'flow_name', 'status', 'created']
    list_filter = ['django_user', 'customer_handle', 'flow_name', 'status']


@admin.register(InstaCredentials)
class InstaCredentialsAdmin(admin.ModelAdmin):
    list_display = ['django_user']


@admin.register(TiktokCredentials)
class TiktokCredentialsAdmin(admin.ModelAdmin):
    list_display = ['django_user']


admin.site.register(InstagramCookies)
admin.site.site_header = "CrazeSocial Administration"


# teams model registration
@admin.register(Teams_data)
class TDA_Admin(admin.ModelAdmin):
    list_display = ['user', 'link']
    search_display = ['user', 'link']
