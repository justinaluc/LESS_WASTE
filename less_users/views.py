from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.views import View
from django.views.generic import ListView, DetailView

from challenges.models import Challenge
from less_users.forms import UserRegisterForm, UserUpdateForm
from less_users.models import UserChallenge, Log


class HomeView(View):
    """>>hello page<< for both: logged-in users and visitors"""

    def get(self, request):
        return render(request, "less_users/home.html")


class RegisterView(View):
    """register new user"""

    def get(self, request):
        if request.user.is_anonymous:
            form = UserRegisterForm()
            return render(request, "less_users/register.html", {"form": form})
        else:
            return redirect("profile")

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Your account >>{user}<< has been created! You can log in now.",
            )
            return redirect("login")
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
        return UserChallenge.objects.select_related("challenge").filter(
            user=self.request.user
        )

    def get(self, request, **kwargs):
        """adds sorting options (ordering by...) of user_challenge items by: >active< >date< or >alphabetically<"""
        my_all = self.get_queryset()
        my_all_count = my_all.count()
        my_active = my_all.filter(is_active=True)
        my_visible = my_all.filter(is_deleted=False)
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
                "my_all_count": my_all_count,
            },
        )

    def post(self, request, **kwargs):
        return render(request, "less_users/my_challenges.html")


class MyChallengeView(LoginRequiredMixin, DetailView):
    """GET: show details of challenge user has taken;
    POST: for active challenges- allows adding points to user's Profile (total points)
    and generate Log object by connecting UserChallenge with now-date;
    for all challenges- allows deleting"""

    model = UserChallenge
    template_name = "less_users/my_challenge.html"

    def get_queryset(self):
        """filters user_challenge queryset to only logged-in user challenges"""
        return UserChallenge.objects.select_related("challenge").filter(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_challenge = self.object
        context["date_now"] = datetime.utcnow().date()
        context["days_left"] = my_challenge.days_left
        context["date_end"] = (
            my_challenge.start_date + timedelta(days=self.object.challenge.duration)
        ).date
        try:
            last_log = my_challenge.log_set.latest("date").date
            date_next = last_log + timedelta(days=my_challenge.challenge.frequency)
            context["last_log"] = last_log.date
            context["date_next"] = date_next.date
        except Log.DoesNotExist:
            context["date_next"] = False
        return context


def activate_view(request, pk):
    """it checks if there exists active user_challenge for logged-in user and chosen challenge;
    if not- it creates new active user_challenge"""
    user_id = request.user
    user_challenge = UserChallenge.objects.filter(
        user=user_id, challenge_id=pk, is_active=True, is_deleted=False
    )
    if user_challenge.exists():
        messages.warning(request, "You still have this challenge active!")
        return redirect("my_challenges")
    else:
        UserChallenge.objects.create(user=user_id, challenge_id=pk)
        messages.success(request, "You activated new challenge!")
        return HttpResponseRedirect(reverse("challenge_detail", args=[str(pk)]))


@login_required
def event_view_done(request):
    """gain points when user challenge is completed by clicking >done< button;
    should check if points can be added (depending on duration and frequency in model)"""
    try:
        challenge_id = int(request.POST.get("done"))
        challenge = Challenge.objects.get(pk=challenge_id)
    except ValueError:
        messages.warning(request, "This challenge does not exist")
    except Challenge.DoesNotExist:
        messages.warning(request, "This challenge does not exist")
    else:
        user = request.user
        user_profile = user.profile
        user_challenges = UserChallenge.objects.filter(
            user_id=user,
            challenge_id=challenge_id,
        )
        if user_challenges.exists():
            latest_challenge = user_challenges.latest("start_date")
            new_points = latest_challenge.get_points()
            if latest_challenge.is_active:
                if new_points:
                    """check previous logs before getting points"""
                    challenge_logs = Log.objects.filter(
                        user_challenge__user_id=user,
                        user_challenge__challenge_id=challenge_id,
                    )
                    if challenge_logs:
                        latest_log = challenge_logs.latest("date")
                        """check if latest log is before or after frequency time"""
                        if (
                            datetime.utcnow().date() - latest_log.date.date()
                        ).days >= challenge.frequency:
                            Log.objects.create(
                                user_challenge=latest_challenge, points=new_points
                            )
                            user_profile.points += new_points
                            user_profile.save()
                            messages.success(
                                request,
                                f"You just gained {new_points} points for this challenge {challenge} again!",
                            )
                        else:
                            messages.warning(
                                request,
                                f"You cannot get points for this challenge {challenge} yet. "
                                f"Frequency is too short from lastly gained points.",
                            )
                    else:
                        Log.objects.create(
                            user_challenge=latest_challenge, points=new_points
                        )
                        user_profile.points += new_points
                        user_profile.save()
                        messages.success(
                            request,
                            f"You just gained first {new_points} points for this challenge {challenge}!",
                        )
                else:
                    messages.warning(
                        request,
                        f"You cannot get points for this challenge {challenge} yet. "
                        f"Frequency is too short from lastly gained points.",
                    )
            else:
                latest_challenge.deactivate(save=True)
                messages.warning(
                    request,
                    f"You cannot get points for this challenge {challenge}. "
                    f"Your challenge is not active anymore.",
                )
        else:
            messages.warning(request, f"You did not activate this challenge yet")
    return redirect("my_challenges")


@login_required
def event_view_stop(request):
    """stop user challenge despite its duration"""
    try:
        user_challenge_id = int(request.POST.get("stop"))
        user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    except ValueError:
        messages.warning(request, "This user_challenge does not exist")
    except UserChallenge.DoesNotExist:
        messages.warning(request, "This user_challenge does not exist")
    else:
        if user_challenge.is_active:
            user_challenge.deactivate(save=True)
            messages.info(
                request,
                f"You stopped challenge: {user_challenge.challenge}. You can activate the new one.",
            )
        else:
            messages.info(
                request,
                f"You have deactivated {user_challenge.challenge} challenge already.",
            )
    return redirect("my_challenges")


@login_required
def event_view_delete(request):
    """delete user_challenge from the list of my challenges"""
    try:
        user_challenge_id = int(request.POST.get("delete"))
        user_challenge = UserChallenge.objects.get(id=user_challenge_id)
    except ValueError:
        messages.warning(request, "This user_challenge does not exist")
    except UserChallenge.DoesNotExist:
        messages.warning(request, "This user_challenge does not exist")
    else:
        if user_challenge.is_deleted:
            messages.info(
                request,
                f"You have already deleted this challenge from your challenges before.",
            )
        else:
            user_challenge = UserChallenge.objects.get(id=user_challenge_id)
            user_challenge.hide(save=True)
            messages.warning(
                request,
                f"You have deleted {user_challenge.challenge} from your challenges.",
            )
    return redirect("my_challenges")


@login_required
def view_events(request):
    if "done" in request.POST:
        event_view_done(request)
    if "stop" in request.POST:
        event_view_stop(request)
    if "delete" in request.POST:
        event_view_delete(request)
    return redirect("my_challenges")
