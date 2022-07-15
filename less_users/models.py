from datetime import date

from django.db import models
from django.contrib.auth.models import User

from challenges.models import Challenge


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} profile'


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT)
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-is_active"]

    def __str__(self):
        return f'{self.user}: {self.challenge.name}'

    @staticmethod
    def todays_day_num():
        """change today's date into integer for further calculations"""
        today = int(date.today().strftime("%Y%m%d"))
        return today

    @property
    def total_points(self):
        """calculate total points for particular user_challenge if any logs were registered"""
        total = 0
        if len(self.log_set.all()) >= 1:
            for log in self.log_set.all():
                total += log.points
        return total

    @property
    def days_left(self):
        """return the rest of the substraction of challenge duration and timedelta between activation date and today;
        ex. duration: 1 month (30 days), activation date: 01.01.2020, today: 28.01.2020.
        gives: 30 - (28 - 1) = 3 """
        start = int(self.start_date.date().strftime("%Y%m%d"))
        today = self.todays_day_num()
        challenge_duration = self.challenge.duration
        days_left = challenge_duration - (today - start)
        return int(days_left)

    @property
    def get_points(self):
        """add points to the particular Log (connected with user_challenge)
        if challenge is active and default frequency passed;
        ex. today: 28.01.2020, last_log: 20.01.2020, frequency: 1/week.
        gives: 28 - 20 > 7 (you can again get points for this challenge,
        because last time you got them over one week ago,
        and this challenge makes possible to get points once for every 7 days;
        for 1/day challenge points can be gained each day"""
        points = self.challenge.points
        if len(self.log_set.all()) > 0:
            last_log = int(self.log_set.last().date.strftime("%Y%m%d"))
        else:
            last_log = 0
        frequency = self.challenge.frequency
        today = self.todays_day_num()
        if today - last_log > frequency:
            return points
        return 0

    def check_if_active(self):
        """check if challenge is not out-of-date; deactivate user_challenge if days_left is less then 0"""
        if self.days_left < 0:
            self.is_active = False
        return self.is_active


class Log(models.Model):
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)

