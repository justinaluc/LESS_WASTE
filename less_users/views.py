from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import View
from django.views.generic import ListView, DetailView

from challenges.models import Challenge
from less_users.forms import UserRegisterForm, UserUpdateForm
from less_users.models import UserChallenge, Profile, Log


class HomeView(View):
    """>>hello page<< for both, logged in and visitors"""
    def get(self, request):
        return render(request, 'less_users/home.html')


class RegisterView(View):
    """register new user"""
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'less_users/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account >>{username}<< has been created! You can log in now.')
        return redirect('home')


class ProfileView(LoginRequiredMixin, View):
    """show user's profile information and update some data when user is logged in
    (user's profile is created automatically by using signals when new user is registered)"""

    def get(self, request):
        """fills form with existing data"""
        u_form = UserUpdateForm(instance=request.user)
        return render(request, 'less_users/profile.html', {'u_form': u_form})

    def post(self, request):
        """enables updating data if form is valid and any changes were made; shows additionaly messages"""
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if any(x in u_form.changed_data for x in ['username', 'email', 'first_name', 'last_name']):
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('profile')
            else:
                messages.warning(request, 'Your account cannot be updated properly... You enetered invalid data!')
                return redirect('profile')
        else:
            messages.warning(request, 'No changes at your account were made.')
        return render(request, 'less_users/profile.html', {'u_form': u_form})


class MyChallengesView(LoginRequiredMixin, ListView):
    """GET: show all challenges user has taken, both active and passed;
       POST: for active challenges- allows adding points to user's Profile (total points)
       and generate Log object by connecting UserChallenge with now-date;
       for all challenges- allows deleting"""
    model = UserChallenge
    template_name = 'less_users/my_challenges.html'
    ordering = ['-start_date']

    def get_queryset(self):
        """filters user_challenge queryset to challenges by logged in user"""
        my_id = self.request.user
        return UserChallenge.objects.filter(user=my_id)

    def get_context_data(self, **kwargs):
        """adds all challenges by logged in user and active ones to the context"""
        context = super().get_context_data(**kwargs)
        context['my_all'] = self.get_queryset()
        context['my_active'] = self.get_queryset().filter(is_active=True)
        return context

    def get(self, request, **kwargs):
        """adds sorting options (ordering by...) of user_challenge items by: >active< >date< or >alphabetically<"""
        my_all = self.get_queryset()
        my_active = self.get_queryset().filter(is_active=True)
        if request.GET.get('order_value'):
            order_value = request.GET.get('order_value')
            my_all = my_all.order_by(order_value)
        return render(request, 'less_users/my_challenges.html', context={'my_all': my_all, 'my_active': my_active})

    def post(self, request, **kwargs):
        return redirect('my_challenges')


class MyChallengeView(LoginRequiredMixin, DetailView):
    """GET: show details of challenge user has taken;
       POST: for active challenges- allows adding points to user's Profile (total points)
       and generate Log object by connecting UserChallenge with now-date;
       for all challenges- allows deleting"""
    model = UserChallenge
    template_name = 'less_users/my_challenge.html'


def activate_view(request, pk):
    """it checks if there exists active user_challenge for logged in user and chosen challenge;
    if not- it creates new active user_challenge"""
    challenge_id = int(request.POST.get('activate'))
    user_challenge_exist = \
        UserChallenge.objects.filter(user=request.user, challenge_id=challenge_id, is_active=True)
    if len(user_challenge_exist) == 0:
        user_new_challenge = UserChallenge.objects.create(user=request.user, challenge_id=challenge_id)
        user_new_challenge.save()
        messages.success(request, 'You activated new challenge!')
        return HttpResponseRedirect(reverse('challenge_detail', args=[str(pk)]))
    else:
        messages.warning(request, 'You still have this challenge active!')
        return redirect('my_challenges')


def event_view(request, **kwargs):
    """gain points when challenge is completed; stop challenge or detele challenge """
    user_id = request.user
    if 'done' in request.POST:
        """should check if points can be added (depending on durration and frequncy in model"""
        challenge_id = int(request.POST.get('done'))
        points = Challenge.objects.get(id=challenge_id).points
        this = UserChallenge.objects.get(user_id=user_id, challenge_id=challenge_id, is_active=True)
        user_challenge_id = this.id
        this.check_if_active()
        if this.get_points == points and this.is_active:
            new_log = Log.objects.create(user_challenge_id=user_challenge_id, points=points)
            my_profile = Profile.objects.get(user_id=user_id)
            my_profile.points += points
            my_profile.save()
            messages.success(request, f'You have got new points {points} for challenge: {this.challenge.name}!')
        elif this.get_points == 0 or this.is_active == False:
            messages.warning(request, f'You cannot get new points for this challenge yet: {this.challenge.name}!')
    elif 'stop' in request.POST:
        user_challenge_id = int(request.POST.get('stop'))
        this = UserChallenge.objects.get(id=user_challenge_id)
        this.is_active = False
        this.save()
        messages.info(request, f'You stopped challenge: {this.challenge.name}. You can activate the new one.')
    elif 'delete' in request.POST:
        user_challenge_id = int(request.POST.get('delete'))
        this = UserChallenge.objects.get(id=user_challenge_id)
        this.delete()
        messages.warning(request, f'You have deleted {this.challenge.name} from your challenges')
    return redirect('my_challenges')



