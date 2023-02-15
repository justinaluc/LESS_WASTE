import pytest

from django.urls import reverse

from less_users.forms import UserRegisterForm


@pytest.mark.django_db
def test_user_register_view_get_unauthorised(client):
    url = reverse("register")
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_register_view_post_unauthorised(client, register_data):
    url = reverse("register")

    response = client.post(url, data=register_data, follow=True)
    messages = list(response.context["messages"])

    assert response.status_code == 200
    assert "You can log in now." in str(messages[0])


def test_user_register_view_get_authorised(client, user):
    client.force_login(user)
    url = reverse("register")

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == "/profile/"


@pytest.mark.django_db
def test_user_register_form_valid():
    form = UserRegisterForm(
        data={
            "username": "Karolina",
            "email": "karola@mail.com",
            "password1": "This!password%321",
            "password2": "This!password%321",
        }
    )

    assert form.is_valid()


TEST_FORM_DATA = [
    (
        "Karol ina",
        "karola@mail.com",
        "This!password%321",
        "This!password%321",
        False,
        "username",
    ),
    ("Karolina", "karola@mail.com", "This!password%321", " ", False, "password2"),
    (
        "Karolina",
        "karola_at_mail.com",
        "This!password%321",
        "This!password%321",
        False,
        "email",
    ),
    ("Karolina", "karola@mail.com", "123", "123", False, "password2"),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, email, password1, password2, result, error", TEST_FORM_DATA
)
def test_user_register_form_invalid(
    username, email, password1, password2, result, error
):
    form = UserRegisterForm(
        data={
            "username": username,
            "email": email,
            "password1": password1,
            "password2": password2,
        }
    )

    assert form.is_valid() is result
    assert list(form.errors)[0] == error


@pytest.mark.django_db
def test_user_register_form_invalid_username_exists(register_data):
    form_1 = UserRegisterForm(data=register_data)
    form_1.is_valid()
    form_1.save()

    assert register_data["username"] == "Karol"

    form_2 = UserRegisterForm(
        data={
            "username": "Karol",
            "email": "karola@mail.com",
            "password1": "This!password%321",
            "password2": "This!password%321",
        }
    )

    assert not form_2.is_valid()
    assert "A user with that username already exists." in form_2.errors["username"]
