from datetime import date, timedelta

from django.db import models
from django.contrib.auth.models import User

from challenges.models import Challenge


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} profile"


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_active"]

    def __str__(self):
        return f"{self.user}: {self.challenge}"

    @property
    def total_points(self):
        """calculate total points for particular user_challenge if any logs were registered"""
        total = 0
        if self.log_set.exists():
            for log in self.log_set.all():
                total += log.points
        return total

    @property
    def get_points(self) -> int:
        """add points to the particular Log (connected with user_challenge)
        if challenge is active and default frequency passed;
        ex. today: 28.01.2020, last_log: 20.01.2020, frequency: 1/week.
        gives: 28 - 20 > 7 (you can again get points for this challenge,
        because last time you got them over one week ago,
        and this challenge makes possible to get points once for every 7 days;
        for 1/day challenge points can be gained each day"""
        points = self.challenge.points
        frequency = self.challenge.frequency
        date_today = date.today()
        self.check_if_active
        if not self.is_active:
            print("_________________runs automaticly if NOT active")  # noqa
            return 0
        if self.log_set.exists():
            print("_________________runs automaticly if active with prev logs")  # noqa
            last_log = self.log_set.last().date
            return points if (date_today - last_log.date()).days >= frequency else 0
        # additional 'elif' condition: user / userchallenge connected with this challenge not active / last log
        else:
            print(
                "_________________runs automatically if active with NO prev logs"
            )  # noqa
            return points

    @property
    def days_left(self) -> int:
        """return the rest of the subtraction of end_date and today;
        to count it, end_date, activation date (start_date)
        and timedelta of challenge duration are summed;
        ex. activation date: 01.01.2020, duration:
        1 month (30 days), today: 28.01.2020.
        (01.01.2020 + timedelta(30)) - 28.01.2020 gives 3 days"""
        end_date = self.start_date.date() + timedelta(days=self.challenge.duration)
        date_today = date.today()
        return (end_date - date_today).days

    @property
    def check_if_active(self) -> bool:
        """check if challenge is not out-of-date;
        deactivate user_challenge if days_left is less than 0"""
        if self.days_left < 0:
            self.is_active = False
        return self.is_active


class Log(models.Model):
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
