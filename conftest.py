import uuid
import pytest
import datetime
from django.contrib.auth.models import User

from challenges.models import Challenge
from less_users.models import UserChallenge


@pytest.fixture(scope='function')
def user(db):
    return User.objects.create_user('Klara_pierwsza', 'klara_the_1@test.com', 'testKlara123')


@pytest.fixture(scope='function')
def test_password():
    return 'testKlara123'


@pytest.fixture(scope='function')
def create_user(db, django_user_model, test_password):
    def make_user(**kwargs):
        kwargs['password'] = test_password

        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture(scope='function')
def challenge_1_day(db):
    return Challenge.objects.create(name='challenge_1_day', description='complete this challenge in 1 day',
                                    duration=1, frequency=1, points=1)


# @pytest.fixture(scope='function')
# def challenge_2_week(db):
#     return Challenge.objects.create('challenge_2_week', 'complete this challenge in 1 week', 7, 7, 2)
#
#
# @pytest.fixture(scope='function')
# def challenge_3_month(db):
#     return Challenge.objects.create('challenge_3_month', 'complete this challenge in 1 month', 28, 7, 5)


# new test of user_challenge activation
@pytest.fixture(scope='function')
def create_user_challenge(db, user, challenge_1_day):
    user = user
    challenge = challenge_1_day
    date = datetime.datetime.now()
    new_challenge = UserChallenge(user=user, challenge=challenge, start_date=date)
    new_challenge.save()
    return new_challenge
