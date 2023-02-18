import pytest

from django.urls import reverse

from less_users.forms import UserUpdateForm, UserRegisterForm


@pytest.mark.django_db
def test_user_update_view_get_unauthorised(client):
    url = reverse("profile")
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == "/login/?next=/profile/"


def test_user_update_view_get_authorised(client, user):
    client.force_login(user)
    url = reverse("profile")

    response = client.get(url)

    assert response.status_code == 200


TEST_UPDATE_DATA = [
    ("Karolina", "karola@mail.com", "Karolina", "Kowalska", True),  # correct
    (
        "Karol ina",
        "karola@mail.com",
        "Karolina",
        "Kowalska",
        False,
    ),  # incorrect: username
    ("Karolina", "karola@mail.com", "", "Kowalska", True),  # correct w/o first_name
    (
        "Karolina",
        "karola_at_mail.com",
        "Karolina",
        "Kowalska",
        False,
    ),  # incorrect: email
    (
        "Karol",
        "karol@mail.com",
        "Karol",
        "Kowalsky",
        False,
    ),  # incorrect: username already exists
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, email, first_name, last_name, result", TEST_UPDATE_DATA
)
def test_user_update_form(
    register_data, username, email, first_name, last_name, result
):
    form_1 = UserRegisterForm(data=register_data)
    form_1.is_valid()
    form_1.save()

    form_2 = UserUpdateForm(
        data={
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
    )

    assert form_2.is_valid() is result


def test_user_update_form_get_filled_with_registered_data(
    client, user, user_register_data
):
    UserRegisterForm(data=user_register_data)

    client.force_login(user)
    url = reverse("profile")

    response = client.get(url)

    form = UserUpdateForm(instance=user)

    assert response.status_code == 200
    assert form["email"].value() == user_register_data["email"]
    assert form["username"].value() == user_register_data["username"]
    assert form["first_name"].value() == ""
