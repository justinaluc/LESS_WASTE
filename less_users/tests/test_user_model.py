from django.contrib.auth.models import User


def test_user_create(user):
    count = User.objects.all().count()
    assert count == 1
