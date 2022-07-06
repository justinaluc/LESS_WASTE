from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import View
from django.views.generic import ListView

from less_users.forms import UserRegisterForm, UserUpdateForm
from less_users.models import UserChallenge

from challenges.models import Challenge


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
        u_form = UserUpdateForm(instance=request.user)
        return render(request, 'less_users/profile.html', {'u_form': u_form})

    def post(self, request):
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
        return render(request, 'less_users/profile.html', {'u_form': u_form})


class MyChallengesView(LoginRequiredMixin, ListView):
    """GET: show all challenges user has taken, both active and passed;
       POST: for active challenges- allow to add points to user's Profile (total points)
       and generate Log object by connecting UserChallenge with now-date;
       for all challenges- allow to delete"""
    model = UserChallenge
    template_name = 'less_users/my_challenges.html'
    paginate_by = 10

    def get(self, request, **kwargs):
        my_id = request.user.id
        my_all = UserChallenge.objects.filter(user=my_id)
        my_active = my_all.filter(is_active=True)
        if request.GET.get('order_value'):
            order_value = request.GET.get('order_value')
            my_all = my_all.order_by(order_value)
        else:
            my_all = my_all.order_by('-is_active', 'challenge__name')
        context = {
            'my_all': my_all,
            'my_active': my_active.count(),
        }
        return render(request, 'less_users/my_challenges.html', context=context)


def activate_view(request, pk):
    """check if logged in user has this challenge active already;
    if not, activate new user_challenge"""
    challenge_id = int(request.POST.get('activate'))
    user_challenge = get_object_or_404(UserChallenge, user=request.user, challenge=challenge_id)
    active = False
    if user_challenge.exists():
        if user_challenge.is_active():
            active = True
            messages.warning(request, 'You still have this challenge active!')
        else:
            active = False
    else:
        new_user_challenge = UserChallenge.objects.create(user=request.user, challenge=challenge_id)
        new_user_challenge.save()
        messages.success(request, 'You activated new challenge!')
    return HttpResponseRedirect(reverse('challenge_detail', args=[str(pk)]))