from django.urls import path
from less_users.views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]