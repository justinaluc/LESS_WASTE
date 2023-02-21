from django.urls import reverse

from less_users.models import UserChallenge


def test_event_stop_flower(client, user):
    url = reverse("event")
    client.force_login(user)
    response = client.post(url, data={"stop": "flower"}, follow=True)

    assert response.status_code == 200
    messages = list(response.context["messages"])
    message = str(messages[0])

    assert len(messages) == 1
    assert message == "This user_challenge does not exist"


def test_event_stop_userchallenge_pk_does_not_exist(client, user, challenge_1_day):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"stop": 1}, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "This user_challenge does not exist" == str(messages[0])


def test_event_stop_userchallenge(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    response = client.post(url, data={"stop": user_challenge.pk}, follow=True)
    user_challenge.refresh_from_db()

    assert not user_challenge.is_active
    assert not user_challenge.is_deleted


def test_event_cannot_stop_deactivated_userchallenge(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month, is_active=False
    )

    response = client.post(url, data={"stop": user_challenge.pk}, follow=True)
    user_challenge.refresh_from_db()
    messages = list(response.context["messages"])

    assert not user_challenge.is_active
    assert not user_challenge.is_deleted
    assert f"You have deactivated {user_challenge.challenge} challenge already." == str(
        messages[0]
    )
