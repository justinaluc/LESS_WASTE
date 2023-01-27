import pytest
from django.urls import reverse


def test_view_home(client):
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_challenges_unauthorised(client, challenges):
    url = reverse("challenge_list")
    response = client.get(url)

    assert response.status_code == 200

    context = response.context

    assert context["object_list"].count() == len(challenges)
    assert set(context["object_list"]) == set(challenges)


@pytest.mark.django_db
def test_view_my_challenges_unauthorised(client):
    url = reverse("my_challenges")
    response = client.get(url)

    assert response.status_code == 302
    assert "/login/?next=/my_challenges/" == response.url


@pytest.mark.django_db
def test_view_my_challenges_authorised(client, user):
    url = reverse("my_challenges")
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
