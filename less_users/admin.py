from django.contrib import admin

from .models import Profile, UserChallenge

admin.site.register(Profile)


class UserChallengeAdmin(admin.ModelAdmin):
    # show below data in user challenge list
    list_display = ('user', 'challenge', 'is_active', 'start_date')

    # add filter for user
    list_filter = ('user',)


admin.site.register(UserChallenge, UserChallengeAdmin)