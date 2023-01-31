import pytest

from less_users.forms import UserRegisterForm, UserUpdateForm
from less_users.models import Profile, UserChallenge, Log


def test_create_user_profile(user):
    profile = user.profile

    assert Profile.objects.filter(id=profile.id).exists()
    assert user.profile.points == 0


@pytest.mark.django_db
def test_create_user_profile_by_user_register_form():
    form = UserRegisterForm(
        data={
            "username": "Karolina_druga",
            "email": "karolina_2@mail.com",
            "password1": "K@rolina_dwadwadwa!czekolada",
            "password2": "K@rolina_dwadwadwa!czekolada",
        }
    )

    assert form.is_valid()


def test_update_user_profile_by_user_update_form(user):
    form = UserUpdateForm(
        instance=user,
        data={
            "username": user.username,
            "email": "Klara_zmienia_adres@email.com",
            "first_name": "Klara",
            "last_name": "Konieczna",
        },
    )
    form.save()

    assert user.email == "Klara_zmienia_adres@email.com"
    assert user.last_name == "Konieczna"


def test_do_not_update_user_profile_invalid_email_in_update_form(user):
    form = UserUpdateForm(
        instance=user,
        data={
            "username": user.username,
            "email": "Klara_zmienia_adres email.com",
        },
    )

    assert not form.is_valid()
    assert "Enter a valid email address." in form.errors["email"]


def test_do_not_update_user_profile_invalid_username_in_update_form(user):
    form = UserUpdateForm(
        instance=user,
        data={
            "username": "Klara zmienia nazwę profilu",
        },
    )

    assert not form.is_valid()
    assert "Enter a valid username" in form.errors["username"][0]


def test_change_user_profile_points_by_clicking_done(user, challenge_2_week):
    user_challenge = UserChallenge.objects.create(user=user, challenge=challenge_2_week)
    user_challenge.check_if_active()
    user_challenge.get_points()

    points = challenge_2_week.points
    Log.objects.create(user_challenge_id=user_challenge.id, points=points)

    my_profile = user.profile
    my_profile.points += points
    my_profile.save()

    assert my_profile.points == points
