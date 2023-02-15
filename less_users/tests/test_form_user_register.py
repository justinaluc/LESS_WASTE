import pytest

from django.urls import reverse

from less_users.forms import UserRegisterForm


@pytest.mark.django_db
def test_form_user_register_correct_unauthorised(client, register_data):
    url = reverse("register")

    response = client.post(url, data=register_data, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "You can log in now." in str(messages[0])


def test_form_user_register_correct_authorised(client, user, register_data):
    client.force_login(user)
    url = reverse("register")

    response = client.post(url, data=register_data)

    assert response.status_code == 302
    assert response.url == "/login/"
