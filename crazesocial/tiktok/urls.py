from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path(
        'home/',
        views.home_page,
        name='tiktok_home'
    ),

    path(
        'json_response/',
        views.tiktok_data_response,
        name='tiktok_data_response'
    ),

    path(
        'json_data/',
        login_required(views.tiktok_extraction_data),
        name='tiktok_extraction_data_view'
    ),

    path(
        'data_save/',
        login_required(views.tiktok_data_save_db),
        name='tiktok_data_save_db'
    ),
]