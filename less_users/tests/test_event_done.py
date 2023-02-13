from datetime import date, timedelta

import pytest

from django.urls import reverse

from freezegun import freeze_time

from less_users.models import UserChallenge, Log


@pytest.mark.django_db
def test_view_events_unauthorised_follow(client):
    url = reverse("event")
    response = client.post(url, follow=True)

    assert response.status_code == 200


@pytest.mark.django_db
def test_view_events_unauthorised(client):
    url = reverse("event")
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == "/login/"


@pytest.mark.django_db
def test_view_events_done_flower(client, user):
    url = reverse("event")
    client.force_login(user)
    response = client.post(url, data={"done": "flower"}, follow=True)

    assert response.status_code == 200
    messages = list(response.context["messages"])

    assert len(messages) == 1

    message = str(messages[0])

    assert message == "This challenge does not exist"


@pytest.mark.django_db
def test_view_events_done_challenge_pk_does_not_exist(client, user):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"done": -1}, follow=True)
    messages = list(response.context["messages"])

    assert "This challenge does not exist" == str(messages[0])


@pytest.mark.django_db
def test_view_events_done_userchallenge_pk_does_not_exist(
    client, user, challenge_1_day
):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"done": challenge_1_day.id}, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "You did not activate this challenge yet" == str(messages[0])


@pytest.mark.django_db
@freeze_time("2023-01-01")
def test_view_events_done_add_points_if_first_log(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    assert not Log.objects.filter(user_challenge=user_challenge).exists()

    response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)
    last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

    assert last_log.points == challenge_3_month.points
    assert last_log.date.date() == date(2023, 1, 1)


@pytest.mark.django_db
def test_view_events_done_add_points_if_frequency_period_passed(
    client, user, challenge_3_month
):
    url = reverse("event")
    client.force_login(user)

    with freeze_time(date(2023, 1, 1)):
        user_challenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        Log.objects.create(
            user_challenge=user_challenge, points=challenge_3_month.points
        )

        assert challenge_3_month.frequency == 7

    with freeze_time(date(2023, 1, 1) + timedelta(days=7)):
        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)
        last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

        assert last_log.points == challenge_3_month.points
        assert last_log.date.date() == date(2023, 1, 8)


@pytest.mark.django_db
def test_view_events_done_add_points_if_frequency_period_not_passed(
    client, user, challenge_3_month
):
    url = reverse("event")
    client.force_login(user)

    with freeze_time(date(2023, 1, 1)):
        user_challenge = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month
        )
        Log.objects.create(
            user_challenge=user_challenge, points=challenge_3_month.points
        )

        assert challenge_3_month.frequency == 7
        assert user_challenge.total_points == 5

    with freeze_time(date(2023, 1, 6)):
        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)

        assert user_challenge.get_points == 0
        assert user_challenge.total_points == 5
        assert Log.objects.filter(user_challenge=user_challenge).latest(
            "date"
        ).date.date() == date(2023, 1, 1)
