from datetime import date, timedelta, datetime

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

    message = str(messages[0])

    assert message == "This challenge does not exist"


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


def test_view_events_done_add_points_if_first_log(client, user, challenge_3_month):
    url = reverse("event")
    client.force_login(user)

    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )

    assert not Log.objects.filter(user_challenge=user_challenge).exists()

    response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)
    latest_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

    assert latest_log.points == challenge_3_month.points
    assert latest_log.date.date() == date.today()


def test_view_events_done_add_0_points_if_frequency_period_did_not_pass(
    client, user, challenge_3_month
):
    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )
    Log.objects.create(user_challenge=user_challenge, points=challenge_3_month.points)
    user.profile.points += challenge_3_month.points
    user.save()

    assert user_challenge.total_points == 5
    assert challenge_3_month.frequency == 7

    with freeze_time(datetime.utcnow() + timedelta(days=6)):
        url = reverse("event")
        client.force_login(user)

        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)
        messages = list(response.context["messages"])
        user.refresh_from_db()
        my_points = user.profile.points

        assert user_challenge.total_points == 5
        assert my_points == challenge_3_month.points
        assert f"You cannot get points" in str(messages[0])


def test_view_events_done_add_points_if_frequency_period_passed(
    client, user, challenge_3_month
):
    user_challenge = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month
    )
    Log.objects.create(user_challenge=user_challenge, points=challenge_3_month.points)
    user.profile.points += challenge_3_month.points
    user.save()

    assert challenge_3_month.frequency == 7

    with freeze_time(datetime.utcnow() + timedelta(days=7)):
        url = reverse("event")
        client.force_login(user)

        response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)
        last_log = Log.objects.filter(user_challenge=user_challenge).latest("date")

        messages = list(response.context["messages"])
        user.refresh_from_db()
        my_points = user.profile.points

        assert my_points == 2 * challenge_3_month.points
        assert last_log.date.date() == date.today()
        assert f"You just gained {challenge_3_month.points} points" in str(messages[0])


def test_view_events_done_active_and_not_active_userchallenges(
    client, user, challenge_3_month
):
    with freeze_time(datetime.utcnow() - timedelta(days=5)):
        user_challenge_1 = UserChallenge.objects.create(
            user=user, challenge=challenge_3_month, is_active=False
        )
        log_1 = Log.objects.create(
            user_challenge=user_challenge_1, points=challenge_3_month.points
        )

        challenge_logs = Log.objects.filter(
            user_challenge__user_id=user, user_challenge__challenge_id=challenge_3_month
        )

        assert challenge_logs.latest("date").date.date() == date.today()
        assert challenge_logs.count() == 1

    user_challenge_2 = UserChallenge.objects.create(
        user=user, challenge=challenge_3_month, is_active=True
    )

    url = reverse("event")
    client.force_login(user)

    response = client.post(url, data={"done": challenge_3_month.pk}, follow=True)

    challenge_logs = Log.objects.filter(
        user_challenge__user_id=user, user_challenge__challenge_id=challenge_3_month
    )

    assert challenge_logs.latest("date").date.date() != date.today()
    assert challenge_logs.count() == 1
