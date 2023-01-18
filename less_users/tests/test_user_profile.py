from less_users.forms import UserRegisterForm, UserUpdateForm
from less_users.models import Profile, UserChallenge, Log


def test_create_user_profile(user):
    profile = user.profile

    assert Profile.objects.filter(id=profile.id).exists()
    assert user.profile.points == 0


def test_create_user_profile_by_user_register_form(user):
    data = {
                "username": user.username,
                "email": user.email,
                "password": user.password,
    }
    form = UserRegisterForm(data)

    assert form.is_valid()


def test_change_user_profile_points_by_clicking_done(user, challenge_2_week):
    my_profile = Profile.objects.get(user_id=user.id)
    user_challenge = UserChallenge.objects.create(user=user, challenge=challenge_2_week)
    user_challenge.check_if_active()
    points = challenge_2_week.points
    user_challenge.get_points()
    new_log = Log.objects.create(user_challenge_id=user_challenge.id, points=points)
    my_profile.points += points
    my_profile.save()

    assert my_profile.points == points

