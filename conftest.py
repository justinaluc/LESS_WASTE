import uuid
import pytest
from django.contrib.auth.models import User


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