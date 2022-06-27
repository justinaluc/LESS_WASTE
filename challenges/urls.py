from django.urls import path

from challenges.views import CategoryListView, ChallengeListView, CategoryDetailView, ChallengeDetailView

urlpatterns = [
    path('category/', CategoryListView.as_view(), name='category_list'),
    path('category/<int:pk>', CategoryDetailView.as_view(), name='category_detail'),
    path('challenge/', ChallengeListView.as_view(), name='challenge_list'),
    path('challenge/<int:pk>', ChallengeDetailView.as_view(), name='challenge_detail'),
]