import pytest
from django.contrib.auth.models import User


def test_user_create(user):
    # User.objects.create_user('Klara_pierwsza', 'klara_the_1@test.com', 'testKlara123')
    count = User.objects.all().count()
    assert count == 1


