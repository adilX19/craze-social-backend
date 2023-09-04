from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views
from . import auth_views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path(
        'home/',
        login_required(views.home_page),
        name='customer_home'
    ),

    path(
        'dashboard/',
        views.dashboard_view,
        name='crazesocial_dashboard'
    ),

    path(
        'extract_data/<flow_name>/',
        views.data_extraction_view,
        name='data_extraction'
    ),

    path(
        'check_status/<flow_name>/',
        views.extraction_status_check_view,
        name='extraction_status_check'
    ),

    path(
        'user_input/',
        views.platform_connect_view,
        name='connect_view'
    ),
    path(
        'account/settings/',
        views.profile_settings_view,
        name='customer_account_settings'
    ),
    path(
        'personal/settings/<flow_name>/',
        views.personal_settings_view,
        name='customer_personal_settings'
    ),
]

# AUTH URL PATTERNS
urlpatterns += [
    path(
        'login/',
        auth_views.LoginView.as_view(),
        name='login_page'
    ),
    path(
        'login/token/refresh/', 
        jwt_views.TokenRefreshView.as_view(), 
        name='token_refresh'
    ),
    path(
        'logout/',
        auth_views.logout_view,
        name='logout_view'
    ),
    path(
        'signup/',
        auth_views.SignUpView.as_view(),
        name='signup_page'
    ),

    path(
        'validate/<str:username>/',
        auth_views.username_validation,
        name='username_validation'
    ),

    path(
        'change-password/',
        auth_views.ChangePasswordView.as_view(),
        name='change_password'
    ),

    path(
        'password_reset/',
        include('django_rest_passwordreset.urls', namespace='password_reset')
    ),

    path(
        'validate_token/<token>/',
        auth_views.custom_validate_password_token,
        name='custom_token_validator'
    ),
]