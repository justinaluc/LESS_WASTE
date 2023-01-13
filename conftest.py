import uuid
import pytest
import datetime
from django.contrib.auth.models import User

from challenges.models import Challenge
from less_users.models import UserChallenge


@pytest.fixture(scope="function")
def user(db):
    return User.objects.create_user(
        "Klara_pierwsza", "klara_the_1@test.com", "testKlara123"
    )


@pytest.fixture(scope="function")
def create_user(db, django_user_model):
    def make_user(**kwargs):
        kwargs["password"] = "testKlara123"

        if "username" not in kwargs:
            kwargs["username"] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture(scope="function")
def challenge_1_day(db):
    return Challenge.objects.create(
        name="challenge_1_day",
        description="complete this challenge in 1 day",
        duration=1,
        frequency=1,
        points=1,
    )


@pytest.fixture(scope="function")
def challenge_2_week(db):
    return Challenge.objects.create(
        name="challenge_2_week",
        description="complete this challenge in 1 week",
        duration=7,
        frequency=7,
        points=2,
    )


@pytest.fixture(scope="function")
def challenge_3_month(db):
    return Challenge.objects.create(
        name="challenge_3_month",
        description="complete this challenge in 1 month",
        duration=30,
        frequency=7,
        points=5,
    )


@pytest.fixture(scope="function")
def challenges(db):
    return [
        Challenge.objects.create(
            name="challenge_3_month",
            description="complete this challenge within 28 days",
            duration=30,
            frequency=7,
            points=5,
        ),
        Challenge.objects.create(
            name="challenge_2_week",
            description="complete this challenge within 7 days",
            duration=7,
            frequency=7,
            points=2,
        ),
        Challenge.objects.create(
            name="challenge_1_day",
            description="complete this challenge within 1 day",
            duration=1,
            frequency=1,
            points=1,
        ),
    ]


# new test of user_challenge activation
@pytest.fixture(scope="function")
def create_user_challenge(db, user, challenge_1_day):
    user = user
    challenge = challenge_1_day
    date = datetime.datetime.now()
    new_challenge = UserChallenge(user=user, challenge=challenge, start_date=date)
    new_challenge.save()
    return new_challenge


@pytest.fixture(scope="function")
def create_user_challenge_month(db, user, challenge_3_month):
    user = user
    challenge = challenge_3_month
    start_date = datetime.datetime.now()
    new_challenge = UserChallenge(user=user, challenge=challenge, start_date=start_date)
    new_challenge.save()
    return new_challenge
