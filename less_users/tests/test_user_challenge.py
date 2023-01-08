from less_users.models import UserChallenge


def test_user_challenge_correct_creation(user, challenge_1_day, create_user_challenge):
    user_challenge = create_user_challenge

    assert user_challenge in UserChallenge.objects.all()
    assert user_challenge.user == user
    assert user_challenge.challenge == challenge_1_day


def test_user_challenge_deactivation(create_user_challenge):
    user_challenge = create_user_challenge
    user_challenge.is_active = False

    assert user_challenge.is_active != True


def test_user_challenge_done(challenge_1_day):
    pass


def test_user_challenge_model_days_left(user, challenge_3_month, create_user_challenge_month):
    user_challenge = create_user_challenge_month




