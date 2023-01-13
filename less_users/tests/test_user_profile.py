from less_users.models import Profile
from less_users.forms import (
    UserRegisterForm,
    UserUpdateForm,
)  # do przyszłego wykorzystania


def test_create_user_profile(user):
    profile = user.profile

    assert Profile.objects.filter(id=profile.id).exists()
    assert user.profile.points == 0


def test_change_user_profile(user):
    profile = user.profile
    profile.points = 10

    assert user.profile.points == 10


def test_change_user_profile_by_user_update_form(user):
    pass
