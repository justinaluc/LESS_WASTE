from freezegun import freeze_time

from datetime import date, timedelta

from less_users.models import UserChallenge, Log


def test_get_points_for_userchallenge_before_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)

    assert not userchallenge.log_set.exists()
    assert userchallenge.get_points() == challenge_3_month.points


def test_get_points_0_for_userchallenge_after_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)
    Log.objects.create(user_challenge=userchallenge, points=userchallenge.get_points())

    assert userchallenge.log_set.count() == 1
    assert userchallenge.get_points() == 0


def test_get_points_for_userchallenge_next_log_after_frequency(user, challenge_3_month):
    with freeze_time(date.today() - timedelta(days=8)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        points = userchallenge.get_points()

        Log.objects.create(user_challenge=userchallenge, points=points)

        assert points == challenge_3_month.points
        assert userchallenge.log_set.count() == 1

    new_points = userchallenge.get_points()

    Log.objects.create(user_challenge=userchallenge, points=new_points)

    assert new_points == challenge_3_month.points
    assert userchallenge.log_set.count() == 2


def test_get_points_0_for_userchallenge_next_log_before_frequency(
    user, challenge_3_month
):
    with freeze_time(date.today() - timedelta(days=5)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        points = userchallenge.get_points()

        Log.objects.create(user_challenge=userchallenge, points=points)

        assert points == challenge_3_month.points
        assert userchallenge.log_set.count() == 1

    new_points = userchallenge.get_points()

    Log.objects.create(user_challenge=userchallenge, points=new_points)

    assert new_points == 0
    assert userchallenge.log_set.count() == 2


def test_get_points_0_for_userchallenge_after_duration_time(user, challenge_3_month):
    with freeze_time(date.today() - timedelta(days=challenge_3_month.duration + 1)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )

    duration = userchallenge.challenge.duration
    points = userchallenge.get_points()

    assert userchallenge.start_date.date() < date.today() - timedelta(days=duration)
    assert points == 0


def test_get_points_0_for_userchallenge_not_active(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month, is_active=False
    )

    assert not userchallenge.is_active

    points = userchallenge.get_points()

    assert points == 0
