import pytest

from freezegun import freeze_time
from datetime import date

from less_users.models import UserChallenge, Log


def test_user_challenge_correct_creation(
    user, challenge_1_day, create_user_challenge_day
):
    user_challenge = create_user_challenge_day

    assert user_challenge in UserChallenge.objects.all()
    assert user_challenge.user == user
    assert user_challenge.challenge == challenge_1_day


@pytest.mark.django_db
@freeze_time("2023-01-01")
def test_user_challenge_deactivation_when_duration_passed(user, challenge_1_day):
    new_challenge = UserChallenge(
        user=user,
        challenge=challenge_1_day,
    )
    new_challenge.save()
    new_challenge.days_left(date_today=date(2023, 1, 5))
    new_challenge.check_if_active()

    assert not new_challenge.is_active


TEST_DIV_DATA = (
    ("2022-12-01", date(2022, 12, 28), 3),
    ("2022-12-31", date(2023, 1, 18), 12),
    ("2023-01-29", date(2023, 3, 1), -1),
    (date.today().strftime("%Y-%m-%d"), date.today(), 30),
)


@pytest.mark.django_db
@pytest.mark.parametrize("a, b, expected", TEST_DIV_DATA)
@pytest.mark.freeze_time
def test_user_challenge_model_days_left_3(
    user, challenge_3_month, a, b, expected, freezer
):
    freezer.move_to(a)
    new_challenge = UserChallenge(user=user, challenge=challenge_3_month)
    new_challenge.save()

    date_today = b
    assert new_challenge.days_left(date_today=date_today) == expected


@pytest.mark.django_db
def test_user_challenge_model_days_left_1(user, challenge_1_day):
    new_challenge = UserChallenge(user=user, challenge=challenge_1_day)
    new_challenge.save()
    new_challenge.check_if_active()

    assert new_challenge.days_left() == 1
    assert new_challenge.is_active


@pytest.mark.django_db
def test_user_challenge_get_points_for_new_challenge_day(
    user, create_user_challenge_day
):
    assert (
        create_user_challenge_day.challenge.points
        == create_user_challenge_day.get_points()
    )


@pytest.mark.django_db
@freeze_time("2023-01-01")
def test_user_challenge_get_points_for_new_challenge_month_after_8_days(
    user, create_user_challenge_month
):
    Log.objects.create(user_challenge=create_user_challenge_month)

    assert (
        create_user_challenge_month.challenge.points
        == create_user_challenge_month.get_points(date_today=date(2023, 1, 9))
    )


@pytest.mark.django_db
@freeze_time("2023-01-01")
def test_user_challenge_do_not_get_points_for_new_challenge_month_after_5_days(
    user, create_user_challenge_month
):
    Log.objects.create(user_challenge=create_user_challenge_month)

    assert (
        not create_user_challenge_month.challenge.points
        == create_user_challenge_month.get_points(date_today=date(2023, 1, 6))
    )
