from less_users.models import Profile
from less_users.forms import UserRegisterForm, UserUpdateForm


def test_create_user_profile(user):
    profile = user.profile

    assert profile in Profile.objects.all()
    assert user.profile.points == 0


def test_change_user_profile(user):
    profile = user.profile
    profile.points = 10

    assert user.profile.points == 10


def test_change_user_profile_by_user_update_form(user):
    pass
