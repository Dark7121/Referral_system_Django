# app/urls.py
from django.urls import path
from .views import register_user, login_user, user_details, referrals

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('user/<str:user_id>/<str:token>/', user_details, name='user_details'),
    path('user/<str:user_id>/<str:token>/referrals/', referrals, name='referrals'),
]
