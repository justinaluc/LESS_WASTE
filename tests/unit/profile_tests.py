from unittest import TestCase
from less_users.models import Profile
from django.contrib.auth.models import User


class ProfileTest(TestCase):
    def test_create_profile(self):
        u = User(
            username="User_one",
            first_name="User",
            last_name="One",
            email="user_1@mail.com",
        )
        p = Profile(user=u)

        self.assertEqual(u, p.user)
        self.assertEqual(0, p.points, "Default points at the beginning should equal 0")

    def test_change_profile(self):
        u = User(
            username="User_one",
            first_name="User",
            last_name="One",
            email="user_1@mail.com",
        )
        p = Profile(user=u)
        p.points = 10

        self.assertEqual(
            10, p.points, "The new points status does not equal points gained"
        )
