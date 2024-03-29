from django.contrib.auth import views as auth_views
from django.urls import path

from less_users.views import HomeView, RegisterView, ProfileView, MyChallengesView, activate_view, event_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='less_users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='less_users/logout.html'), name='logout'),
    path('my_challenges/', MyChallengesView.as_view(template_name='less_users/my_challenges.html'), name='my_challenges'),
    path('activate/<int:pk>/', activate_view, name='activate_challenge'),
    path('event/', event_view, name='event'),
]