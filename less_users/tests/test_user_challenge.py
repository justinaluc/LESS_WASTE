import pytest

from freezegun import freeze_time

from datetime import date, timedelta

from less_users.models import UserChallenge, Log


def test_user_challenge_correct_creation(
    user, challenge_1_day, create_user_challenge_day
):
    user_challenge = create_user_challenge_day

    assert user_challenge in UserChallenge.objects.all()
    assert user_challenge.user == user
    assert user_challenge.challenge == challenge_1_day


def test_user_challenge_deactivation_when_duration_passed(user, challenge_1_day):
    with freeze_time(date(2023, 1, 1)):
        new_challenge = UserChallenge(
            user=user,
            challenge=challenge_1_day,
        )
        new_challenge.save()

    with freeze_time(date(2023, 1, 5)):
        new_challenge.check_if_active

        assert not new_challenge.is_active


TEST_DIV_DATA = (
    ("2022-12-01", "2022-12-28", 3),
    ("2022-12-31", "2023-01-18", 12),
    ("2023-01-29", "2023-03-01", -1),
    (date.today(), date.today(), 30),
)


@pytest.mark.parametrize("date_start, date_today, expected", TEST_DIV_DATA)
def test_user_challenge_model_days_left_3(
    user, challenge_3_month, date_start, date_today, expected
):
    with freeze_time(date_start):
        new_challenge = UserChallenge(user=user, challenge=challenge_3_month)
        new_challenge.save()

    with freeze_time(date_today):
        assert new_challenge.days_left == expected


def test_user_challenge_model_days_left_1(user, challenge_1_day):
    new_challenge = UserChallenge(user=user, challenge=challenge_1_day)
    new_challenge.save()
    new_challenge.check_if_active

    assert new_challenge.days_left == 1
    assert new_challenge.is_active


def test_user_challenge_get_points_for_new_challenge_day(user, challenge_1_day):
    user_challenge = UserChallenge.objects.create(user=user, challenge=challenge_1_day)
    user_log = Log.objects.create(
        user_challenge=user_challenge, points=challenge_1_day.points
    )

    user_challenge.get_points

    assert user_challenge.challenge.points == user_log.points


def test_user_challenge_get_points_for_new_challenge_month_after_8_days(
    user, challenge_3_month
):
    with freeze_time(date.today()):
        user_challenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )

        assert user_challenge.total_points == 0

    with freeze_time(date.today() + timedelta(days=8)):
        user_log = Log.objects.create(
            user_challenge=user_challenge, points=challenge_3_month.points
        )

        assert user_challenge.total_points == user_log.points
