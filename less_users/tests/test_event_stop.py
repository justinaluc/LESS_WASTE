from django.urls import reverse

from less_users.models import UserChallenge


def test_event_stop_userchallenge_not_active(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    response = client.post(url, data={"stop": user_challenge.pk}, follow=True)
    user_challenge.refresh_from_db()

    assert not user_challenge.is_active
