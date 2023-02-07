from django.db import models


class Challenge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.IntegerField(help_text="how long it takes to complete challenge")
    frequency = models.IntegerField(
        help_text="how often challenge is activated: " "1/day, 1/week, 1/month, 1/year"
    )
    points = models.IntegerField(
        help_text="how many points are gained " "each time challenge is completed"
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    challenges = models.ManyToManyField(Challenge, through="CategoryChallenge")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class CategoryChallenge(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category}: {self.challenge}"

    class Meta:
        verbose_name_plural = "Challenges categories"
