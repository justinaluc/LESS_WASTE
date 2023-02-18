from datetime import date, timedelta

from freezegun import freeze_time

from less_users.models import UserChallenge, Log


def test_total_points_for_userchallenge_before_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)

    assert userchallenge.total_points == 0


def test_total_points_for_userchallenge_after_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)
    points = userchallenge.get_points()
    Log.objects.create(user_challenge=userchallenge, points=points)

    assert userchallenge.total_points == 5


def test_total_points_for_userchallenge_next_log_after_frequency(
    user, challenge_3_month
):
    with freeze_time(date.today() - timedelta(days=8)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        points_1 = userchallenge.get_points()
        Log.objects.create(user_challenge=userchallenge, points=points_1)

        assert points_1 == 5
        assert userchallenge.total_points == points_1

    points_2 = userchallenge.get_points()
    Log.objects.create(user_challenge=userchallenge, points=points_2)

    assert points_2 == 5
    assert userchallenge.total_points == points_1 + points_2


def test_total_points_for_userchallenge_next_log_before_frequency(
    user, challenge_3_month
):
    with freeze_time(date.today() - timedelta(days=5)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        points_1 = userchallenge.get_points()
        Log.objects.create(user_challenge=userchallenge, points=points_1)

        assert points_1 == 5
        assert userchallenge.total_points == points_1

    points_2 = userchallenge.get_points()
    Log.objects.create(user_challenge=userchallenge, points=points_2)

    assert points_2 == 0
    assert userchallenge.total_points == points_1 + points_2
