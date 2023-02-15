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

    assert userchallenge.check_if_active


def test_check_if_active_after_duration_time(user, challenge_3_month):
    with freeze_time(date.today() - timedelta(days=challenge_3_month.duration + 1)):
        userchallenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )

    assert not userchallenge.check_if_active


def test_check_if_not_active_when_deactivated(user, challenge_3_month):
    userchallenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month, is_active=False
    )

    assert not userchallenge.check_if_active
