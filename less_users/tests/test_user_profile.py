from less_users.models import Profile


def test_profile_user_create(user):
    profile = user.profile

    assert profile in Profile.objects.all()
    assert user.profile.points == 0
