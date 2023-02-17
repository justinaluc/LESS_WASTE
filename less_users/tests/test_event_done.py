from datetime import date, timedelta

from django.urls import reverse

from freezegun import freeze_time

from less_users.models import UserChallenge, Log


def test_view_events_unauthorised_follow(client):
    url = reverse("event")
    response = client.post(url, follow=True)

    assert response.status_code == 200


def test_view_events_unauthorised(client):
    url = reverse("event")
    response = client.post(url)

    print(response.url)
    assert response.status_code == 302
    assert response.url == "/login/?next=/event/"


def test_view_events_done_flower(client, user):
    url = reverse("event")
    client.force_login(user)
    response = client.post(url, data={"done": "flower"}, follow=True)

    assert response.status_code == 200
    messages = list(response.context["messages"])

    assert len(messages) == 1

    assert "This challenge does not exist" == str(messages[0])


def test_view_events_done_challenge_pk_does_not_exist(client, user):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"done": -1}, follow=True)
    messages = list(response.context["messages"])

    assert "This challenge does not exist" == str(messages[0])


def test_view_events_done_userchallenge_pk_does_not_exist(
    client, user, challenge_1_day
):
    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"done": challenge_1_day.id}, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "You did not activate this challenge yet" == str(messages[0])


@freeze_time("2023-01-01")
def test_view_events_done_add_points_if_first_log(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    assert not Log.objects.filter(user_challenge=user_challenge).exists()

    response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)

    assert response.status_code == 200

    last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

    assert last_log.points == challenge_3_month.points
    assert last_log.date.date() == date(2023, 1, 1)


def test_view_events_done_add_points_if_frequency_period_passed(
    client, user, challenge_3_month
):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )
    Log.objects.create(user_challenge=user_challenge, points=challenge_3_month.points)
    last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

    assert last_log.points == challenge_3_month.points
    assert last_log.date.date() == date.today()

    assert challenge_3_month.frequency == 7

    with freeze_time(date.today() + timedelta(days=7)):
        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)

        last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

        assert last_log.points == challenge_3_month.points
        assert last_log.date.date() == date.today()


def test_view_events_done_add_points_if_frequency_period_did_not_pass(
    client, user, challenge_3_month
):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )
    Log.objects.create(user_challenge=user_challenge, points=challenge_3_month.points)

    assert challenge_3_month.frequency == 7
    assert user_challenge.total_points == 5

    with freeze_time(date.today() + timedelta(days=3)):
        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)

        assert user_challenge.get_points() == 0
        assert user_challenge.total_points == 5
        assert Log.objects.filter(user_challenge=user_challenge).latest(
            "date"
        ).date.date() == date.today() - timedelta(days=3)
