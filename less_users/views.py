from datetime import date

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
    """>>hello page<< for both: logged-in users and visitors"""

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
            user = form.save()
            messages.success(
                request,
                f"Your account >>{user}<< has been created! You can log in now.",
            )
            return redirect("home")
        return render(request, "less_users/register.html", {"form": form})


class ProfileView(LoginRequiredMixin, View):
    """show user's profile information and update some data when user is logged in
    (user's profile is created automatically by using signals when new user is registered)"""

    def get(self, request):
        """fills form with existing data"""
        u_form = UserUpdateForm(instance=request.user)
        return render(request, "less_users/profile.html", {"u_form": u_form})

    def post(self, request):
        """enables updating data if form is valid and any changes were made; shows additional messages"""
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.has_changed():
            if u_form.is_valid():
                u_form.save()
                messages.success(request, "Your account has been updated!")
                return redirect("profile")
            else:
                messages.warning(
                    request,
                    "Your account cannot be updated properly... You entered invalid data!",
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
        """filters user_challenge queryset to only logged-in user challenges"""
        return UserChallenge.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """adds all, active ones and not deleted challenges of logged-in user to the context"""
        context = super().get_context_data(**kwargs)
        context["my_all"] = self.get_queryset()
        context["my_active"] = self.get_queryset().filter(is_active=True)
        context["my_visible"] = self.get_queryset().filter(is_deleted=False)
        return context

    def get(self, request, **kwargs):
        """adds sorting options (ordering by...) of user_challenge items by: >active< >date< or >alphabetically<"""
        my_all = self.get_queryset()
        my_active = my_all.filter(is_active=True)
        my_visible = my_all.filter(is_deleted=False)
        # check order value set from web page -> has to be fixed !!!!!!!!!!!!
        if request.GET.get("order_value"):
            order_value = request.GET.get("order_value")
            my_all = my_all.order_by(order_value)
        return render(
            request,
            "less_users/my_challenges.html",
            context={
                "my_all": my_all,
                "my_active": my_active,
                "my_visible": my_visible,
            },
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
    """it checks if there exists active user_challenge for logged-in user and chosen challenge;
    if not- it creates new active user_challenge"""
    user_challenge = UserChallenge.objects.filter(
        user=request.user, challenge_id=pk, is_active=True, is_deleted=False
    )
    if user_challenge.exists():
        messages.warning(request, "You still have this challenge active!")
        return redirect("my_challenges")
    else:
        UserChallenge.objects.create(user=request.user, challenge_id=pk)
        messages.success(request, "You activated new challenge!")
        return HttpResponseRedirect(reverse("challenge_detail", args=[str(pk)]))


def event_view_done(request):
    """gain points when user challenge is completed by clicking >done< button;
    should check if points can be added (depending on duration and frequency in model)"""
    try:
        challenge_id = int(request.POST.get("done"))
    except ValueError:
        messages.warning(request, f"This challenge does not exist")
    else:
        if Challenge.objects.filter(pk=challenge_id).exists():
            points = Challenge.objects.get(pk=challenge_id).points
            user_challenge = UserChallenge.objects.get(
                user_id=request.user,
                challenge_id=challenge_id,
                is_active=True,
                is_deleted=False,
            )
            # user_challenge.check_if_active(date_today=date.today())
            if user_challenge.is_active:
                """proceed user getting points for user challenge; it is up to date"""
                new_points = user_challenge.get_points()
                if new_points == points:
                    Log.objects.create(
                        user_challenge_id=user_challenge.id, points=points
                    )
                    my_profile = request.user.profile
                    my_profile.points += points
                    my_profile.save()
                    messages.success(
                        request,
                        f"You have just got {new_points} points for challenge: {user_challenge.challenge}!",
                    )
                else:
                    messages.warning(
                        request,
                        f"You cannot get new points for this challenge yet: {user_challenge.challenge}. "
                        f"You have already done it within last {user_challenge.challenge.frequency} days",
                    )
            else:
                """stop user challenge is out of date"""
                user_challenge.is_active = False
                user_challenge.save()
                messages.warning(
                    request,
                    f"You cannot get new points for this challenge: {user_challenge.challenge}. "
                    f"Its duration time passed",
                )
        else:
            messages.warning(request, f"This challenge does not exist")
    return redirect("my_challenges")


def event_view_stop(request):
    """stop user challenge despite its duration"""
    user_challenge_id = int(request.POST.get("stop"))
    user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    user_challenge.is_active = False
    user_challenge.save()
    messages.info(
        request,
        f"You stopped challenge: {user_challenge.challenge}. You can activate the new one.",
    )
    return redirect("my_challenges")


def event_view_delete(request):
    """delete user challenge from the list of my challenges (hide it with 'is_deleted' parameter set into True)"""
    user_challenge_id = int(request.POST.get("delete"))
    user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    user_challenge.is_active = False
    user_challenge.is_deleted = True
    user_challenge.save()
    messages.warning(
        request, f"You have deleted {user_challenge.challenge} from your challenges."
    )
    return redirect("my_challenges")


def view_events(request):
    if "done" in request.POST:
        event_view_done(request)
    if "stop" in request.POST:
        event_view_stop(request)
    if "delete" in request.POST:
        event_view_delete(request)
    return redirect("my_challenges")
