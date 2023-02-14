import pytest
from django.urls import reverse
from freezegun import freeze_time

from datetime import date, timedelta

from less_users.models import UserChallenge


def test_check_if_active_before_duration_time(user, challenge_3_month):
    with freeze_time(date.today() - timedelta(days=challenge_3_month.duration - 1)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )

    userchallenge.check_if_active

    assert userchallenge.is_active


def test_check_if_active_after_duration_time(user, challenge_3_month):
    with freeze_time(date.today() - timedelta(days=challenge_3_month.duration + 1)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )

    userchallenge.check_if_active

    assert not userchallenge.is_active


def test_check_if_not_active_when_deactivated(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(user=user, challenge=challenge_3_month)
    userchallenge.is_active = False
    userchallenge.check_if_active

    assert not userchallenge.is_active


@pytest.mark.skip
def test_check_if_active_when_stopped(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    response = client.post(url, data={"stop": user_challenge.pk}, follow=True)

    assert not user_challenge.is_active
