import pytest
from datetime import date, timedelta

from less_users.models import UserChallenge


def test_user_challenge_correct_creation(user, challenge_1_day, create_user_challenge):
    user_challenge = create_user_challenge

    assert user_challenge in UserChallenge.objects.all()
    assert user_challenge.user == user
    assert user_challenge.challenge == challenge_1_day


@pytest.mark.django_db
def test_user_challenge_deactivation_when_duration_passed(user, challenge_1_day):
    user = user
    challenge = challenge_1_day
    start_date = date.today() - timedelta(days=3)
    new_challenge = UserChallenge(user=user, challenge=challenge, start_date=start_date)
    new_challenge.save()

    assert new_challenge.check_if_active != True


def test_user_challenge_done(challenge_1_day):
    pass


@pytest.mark.django_db
def test_user_challenge_model_days_left_3(user, challenge_3_month):
    user = user
    challenge = challenge_3_month
    start_date = date.today() - timedelta(days=27)
    new_challenge = UserChallenge(user=user, challenge=challenge, start_date=start_date)
    new_challenge.save()

    assert new_challenge.days_left == 3




