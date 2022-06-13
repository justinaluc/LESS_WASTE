from django.urls import path
from less_users import views


urlpatterns = [
    path('', views.home, name='home'),
]