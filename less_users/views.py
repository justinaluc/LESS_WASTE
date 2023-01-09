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
    """>>hello page<< for both: logged in users and visitors"""

    def get(self, request):
        return render(request, "less_users/home.html")


class RegisterView(View):
    """register new user"""

    def get(self, request):
        form = UserRegisterForm()
        return render(request, "less_users/register.html", {"form": form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Your account >>{username}<< has been created! You can log in now.",
            )
        return redirect("home")


class ProfileView(LoginRequiredMixin, View):
    """show user's profile information and update some data when user is logged in
    (user's profile is created automatically by using signals when new user is registered)"""

    def get(self, request):
        """fills form with existing data"""
        u_form = UserUpdateForm(instance=request.user)
        return render(request, "less_users/profile.html", {"u_form": u_form})

    def post(self, request):
        """enables updating data if form is valid and any changes were made; shows additionaly messages"""
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if any(
            x in u_form.changed_data
            for x in ["username", "email", "first_name", "last_name"]
        ):
            if u_form.is_valid():
                u_form.save()
                messages.success(request, "Your account has been updated!")
                return redirect("profile")
            else:
                messages.warning(
                    request,
                    "Your account cannot be updated properly... You enetered invalid data!",
                )
                return redirect("profile")
        else:
            messages.warning(request, "No changes at your account were made.")
        return render(request, "less_users/profile.html", {"u_form": u_form})


class MyChallengesView(LoginRequiredMixin, ListView):
    """GET: show all challenges user has taken, both active and passed;
    POST: for active challenges- allows adding points to user's Profile (total points)
    and generate Log object by connecting UserChallenge with now-date;
    for all challenges- allows deleting"""

    model = UserChallenge
    template_name = "less_users/my_challenges.html"
    ordering = ["-start_date"]

    def get_queryset(self):
        """filters user_challenge queryset to challenges by logged in user"""
        my_id = self.request.user
        return UserChallenge.objects.filter(user=my_id)

    def get_context_data(self, **kwargs):
        """adds all challenges by logged in user and active ones to the context"""
        context = super().get_context_data(**kwargs)
        context["my_all"] = self.get_queryset()
        context["my_active"] = self.get_queryset().filter(is_active=True)
        return context

    def get(self, request, **kwargs):
        """adds sorting options (ordering by...) of user_challenge items by: >active< >date< or >alphabetically<"""
        my_all = self.get_queryset()
        my_active = self.get_queryset().filter(is_active=True)
        if request.GET.get("order_value"):
            order_value = request.GET.get("order_value")
            my_all = my_all.order_by(order_value)
        return render(
            request,
            "less_users/my_challenges.html",
            context={"my_all": my_all, "my_active": my_active},
        )

    def post(self, request, **kwargs):
        return redirect("my_challenges")


class MyChallengeView(LoginRequiredMixin, DetailView):
    """GET: show details of challenge user has taken;
    POST: for active challenges- allows adding points to user's Profile (total points)
    and generate Log object by connecting UserChallenge with now-date;
    for all challenges- allows deleting"""

    model = UserChallenge
    template_name = "less_users/my_challenge.html"


def activate_view(request, pk):
    """it checks if there exists active user_challenge for logged in user and chosen challenge;
    if not- it creates new active user_challenge"""
    user_challenge_exist = UserChallenge.objects.filter(
        user=request.user, challenge_id=pk, is_active=True
    )
    if user_challenge_exist.exists():
        messages.warning(request, "You still have this challenge active!")
        return redirect("my_challenges")
    else:
        user_new_challenge = UserChallenge.objects.create(user=request.user, challenge_id=pk)
        user_new_challenge.save()
        messages.success(request, "You activated new challenge!")
        return HttpResponseRedirect(reverse("challenge_detail", args=[str(pk)]))


def event_view(request, **kwargs):
    """gain points when challenge is completed; stop challenge or delete challenge"""
    user_id = request.user
    if "done" in request.POST:
        """should check if points can be added (depending on duration and frequency in model"""
        challenge_id = int(request.POST.get("done"))
        points = Challenge.objects.get(id=challenge_id).points
        user_challenge = UserChallenge.objects.get(
            user_id=user_id, challenge_id=challenge_id, is_active=True
        )
        user_challenge_id = user_challenge.id
        user_challenge.check_if_active()
        if user_challenge.get_points == points and user_challenge.is_active:
            new_log = Log.objects.create(
                user_challenge_id=user_challenge_id, points=points
            )
            my_profile = Profile.objects.get(user_id=user_id)
            my_profile.points += points
            my_profile.save()
            messages.success(
                request,
                f"You have got new points {points} for challenge: {user_challenge.challenge}!",
            )
        elif user_challenge.get_points == 0 or user_challenge.is_active == False:
            messages.warning(
                request,
                f"You cannot get new points for this challenge yet: {user_challenge.challenge}!",
            )
    elif "stop" in request.POST:
        user_challenge_id = int(request.POST.get("stop"))
        user_challenge = UserChallenge.objects.get(id=user_challenge_id)
        user_challenge.is_active = False
        user_challenge.save()
        messages.info(
            request,
            f"You stopped challenge: {user_challenge.challenge}. You can activate the new one.",
        )
    elif "delete" in request.POST:
        user_challenge_id = int(request.POST.get("delete"))
        user_challenge = UserChallenge.objects.get(id=user_challenge_id)
        user_challenge.delete()
        messages.warning(
            request, f"You have deleted {user_challenge.challenge} from your challenges"
        )
    return redirect("my_challenges")
