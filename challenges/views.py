from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin

from less_users.models import UserChallenge
from .models import Challenge, Category

# mixin with additional, filtered by logged in user, context used in many views:


class ExtraUserChallengeContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(ExtraUserChallengeContextMixin, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            context['my_challenges'] = None
        else:
            my_active = UserChallenge.objects.filter(user=self.request.user, is_active=True)
            my_challenges = []
            for each in my_active:
                my_challenges.append(each.challenge)
            context['my_challenges'] = my_challenges
        return context

# views for CATEGORY functionalities:


class CategoryListView(ListView):
    """generic ListView to list all categories of challenges"""
    model = Category
    ordering = ['name']


class CategoryDetailView(ExtraUserChallengeContextMixin, DetailView):
    """generic DetailView to show challenges in particular category"""
    model = Category

# views for CHALLENGE functionalities:


class ChallengeListView(ExtraUserChallengeContextMixin, ListView):
    """generic ListView to list all categories of challenges"""
    model = Challenge
    ordering = ['name']
    paginate_by = 12


class ChallengeDetailView(ExtraUserChallengeContextMixin, DetailView):
    """generic DetailView to show category with its details"""
    model = Challenge



