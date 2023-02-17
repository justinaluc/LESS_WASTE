from datetime import timedelta, datetime

from less_users.models import UserChallenge


def test_check_if_active_before_duration_time(user, challenge_3_month):
    start_date = datetime.utcnow() - timedelta(days=challenge_3_month.duration - 1)
    userchallenge = UserChallenge(
        user=user, challenge=challenge_3_month, start_date=start_date
    )

    assert userchallenge.check_if_active
    assert userchallenge.start_date == start_date


def test_check_if_active_after_duration_time(user, challenge_3_month):
    start_date = datetime.utcnow() - timedelta(days=challenge_3_month.duration + 1)
    userchallenge = UserChallenge(
        user=user, challenge=challenge_3_month, start_date=start_date
    )

    assert not userchallenge.check_if_active
    assert userchallenge.start_date == start_date


def test_check_if_not_active_when_deactivated(user, challenge_3_month):
    userchallenge = UserChallenge(
        user=user,
        challenge=challenge_3_month,
        is_active=False,
        start_date=datetime.utcnow(),
    )

    assert not userchallenge.check_if_active
