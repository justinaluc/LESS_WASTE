from datetime import date, timedelta

from freezegun import freeze_time

from less_users.models import UserChallenge, Log


def test_total_points_for_userchallenge_before_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)

    assert userchallenge.total_points == 0


def test_total_points_for_userchallenge_after_first_log(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)
    Log.objects.create(user_challenge=userchallenge, points=userchallenge.get_points())

    assert userchallenge.total_points == challenge_3_month.points


def test_total_points_for_userchallenge_next_log_after_frequency(
    user, challenge_3_month
):
    with freeze_time(date.today() - timedelta(days=8)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        Log.objects.create(
            user_challenge=userchallenge, points=userchallenge.get_points()
        )

        assert userchallenge.total_points == challenge_3_month.points

    with freeze_time(date.today()):
        Log.objects.create(
            user_challenge=userchallenge, points=userchallenge.get_points()
        )

        assert userchallenge.log_set.count() == 2
        assert userchallenge.total_points == 2 * challenge_3_month.points


def test_total_points_for_userchallenge_next_log_before_frequency(
    user, challenge_3_month
):
    with freeze_time(date.today() - timedelta(days=5)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        Log.objects.create(
            user_challenge=userchallenge, points=userchallenge.get_points()
        )

        assert userchallenge.log_set.count() == 1
        assert userchallenge.total_points == challenge_3_month.points

    with freeze_time(date.today()):
        Log.objects.create(
            user_challenge=userchallenge, points=userchallenge.get_points()
        )

        assert userchallenge.log_set.count() == 2
        assert userchallenge.total_points == challenge_3_month.points