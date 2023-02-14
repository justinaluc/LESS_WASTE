from django.urls import reverse

from less_users.models import UserChallenge


def test_view_home(client):
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200


def test_view_challenges_unauthorised(client, challenges):
    url = reverse("challenge_list")
    response = client.get(url)

    assert response.status_code == 200

    context = response.context

    assert context["object_list"].count() == len(challenges)
    assert set(context["object_list"]) == set(challenges)


def test_view_challenges_with_my_challenges_active_when_authorised(
    client, user, challenges
):
    UserChallenge.objects.create(user=user, challenge=challenges[0])
    UserChallenge.objects.create(user=user, challenge=challenges[1])

    url = reverse("challenge_list")
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200

    context = response.context
    print(set(context["my_challenges"]))
    print(set(challenges))

    assert len(context["my_challenges"]) == 2
    assert len(challenges) == 3
    assert not set(context["my_challenges"]) == set(challenges)


def test_view_my_challenges_unauthorised(client):
    url = reverse("my_challenges")
    response = client.get(url)

    assert response.status_code == 302
    assert "/login/?next=/my_challenges/" == response.url


def test_view_my_challenges_authorised(client, user):
    url = reverse("my_challenges")
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


def test_view_activate_user_challenge(client, user, challenge_1_day):
    url = reverse("activate_challenge", args=[challenge_1_day.pk])
    client.force_login(user)

    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert (
        UserChallenge.objects.filter(user=user)
        .filter(challenge=challenge_1_day)
        .exists()
    )
