from django.urls import reverse

from less_users.models import UserChallenge


def test_event_delete_flower(client, user):
    url = reverse("event")
    client.force_login(user)
    response = client.post(url, data={"delete": "flower"}, follow=True)

    assert response.status_code == 200
    messages = list(response.context["messages"])
    message = str(messages[0])

    assert len(messages) == 1
    assert message == "This user_challenge does not exist"


def test_event_delete_userchallenge_pk_does_not_exist(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"delete": 1}, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "This user_challenge does not exist" == str(messages[0])


def test_event_delete_userchallenge(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    response = client.post(url, data={"delete": user_challenge.pk}, follow=True)
    user_challenge.refresh_from_db()

    assert not user_challenge.is_active
    assert user_challenge.is_deleted


def test_event_delete_cannot_delete_deleted_userchallenge(
    client, user, challenge_3_month
):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month, is_active=False, is_deleted=True
    )

    response = client.post(url, data={"delete": user_challenge.pk}, follow=True)
    user_challenge.refresh_from_db()
    messages = list(response.context["messages"])

    assert not user_challenge.is_active
    assert user_challenge.is_deleted
    assert (
        "You have already deleted this challenge from your challenges before."
        == str(messages[0])
    )
