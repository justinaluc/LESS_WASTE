from django.contrib.auth.models import User


def test_user_create(user):
    # User.objects.create_user('Klara_pierwsza', 'klara_the_1@test.com', 'testKlara123')
    count = User.objects.all().count()
    assert count == 1


def test_check_password(create_user):
    # u.set_password, u.check_password
    user = User.objects.create_user("test", "test@test.com", "test123")
    user.set_password("secret")
    assert user.check_password("secret") is True
