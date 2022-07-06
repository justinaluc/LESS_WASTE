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

# views for CHALLENGE functionalities:


class ChallengeListView(ListView):
    """generic ListView to list all categories of challenges"""
    model = Challenge
    ordering = ['name']
    paginate_by = 12


class ChallengeDetailView(DetailView):
    """generic DetailView to show category with its details"""
    model = Challenge

    # def get_context_data(self, *args, **kwargs):
    # """add to context information about active challenge for logged in user"""
    #     active = UserChallenge.objects.filter(user=self.request.user.id)
    #     context = super(ChallengeDetailView, self).get_context_data()
    #     context['active'] = active
    #     return context
    #

