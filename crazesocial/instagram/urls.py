from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path(
        'home/',
        views.home_page,
        name='instagram_home'
    ),

    path(
        'json_response/',
        views.instagram_data_response,
        name='instagram_data_response'
    ),

    path(
        'json_data/',
        login_required(views.insta_extraction_data),
        name='insta_extraction_data_view'
    ),

    path(
        'data_save/',
        login_required(views.insta_data_save_db),
        name='insta_data_save_db'
    ),
]