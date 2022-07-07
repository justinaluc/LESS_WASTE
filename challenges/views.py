from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

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

