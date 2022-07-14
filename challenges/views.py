from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from less_users.models import UserChallenge
from .models import Challenge, Category
# from less_users.models import UserChallenge, Profile, Log


# views for CATEGORY functionalities:


class CategoryListView(ListView):
    """generic ListView to list all categories of challenges"""
    model = Category
    ordering = ['name']


class CategoryDetailView(DetailView):
    """generic DetailView to show challenges in particular category"""
    model = Category

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['my_challenges'] = None
        else:
            my_active = UserChallenge.objects.filter(user=self.request.user, is_active=True)
            my_challenges = []
            for each in my_active:
                my_challenges.append(each.challenge)
            context['my_challenges'] = my_challenges
        return context


# views for CHALLENGE functionalities:


class ChallengeListView(ListView):
    """generic ListView to list all categories of challenges"""
    model = Challenge
    ordering = ['name']
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(ChallengeListView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['my_challenges'] = None
        else:
            my_active = UserChallenge.objects.filter(user=self.request.user, is_active=True)
            my_challenges = []
            for each in my_active:
                my_challenges.append(each.challenge)
            context['my_challenges'] = my_challenges
        return context


class ChallengeDetailView(DetailView):
    """generic DetailView to show category with its details"""
    model = Challenge

    def get_context_data(self, **kwargs):
        context = super(ChallengeDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['my_challenges'] = None
        else:
            my_active = UserChallenge.objects.filter(user=self.request.user, is_active=True)
            my_challenges = []
            for each in my_active:
                my_challenges.append(each.challenge)
            context['my_challenges'] = my_challenges
        return context

