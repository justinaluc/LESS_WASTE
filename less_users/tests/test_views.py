import pytest as pytest
from django.urls import reverse

from challenges.models import Category, Challenge


def test_view_home(client):
    url = reverse('home')
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_challenges_unauthorised(client, challenges):
    url = reverse('challenge_list')
    response = client.get(url)

    assert response.status_code == 200

    context = response.context

    assert context['object_list'].count() == len(challenges)

    for challenge in challenges:
        assert challenge in context['object_list']


@pytest.mark.django_db
def test_view_my_challenges_unauthorised(client):
    url = reverse('my_challenges')
    response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_view_my_challenges_authorised(client, user):
    url = reverse('my_challenges')
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200

