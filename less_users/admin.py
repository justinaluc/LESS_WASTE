from django.contrib import admin

from .models import Profile, UserChallenge, Log


class LogInline(admin.TabularInline):
    model = Log
    extra = 2


class UserChallengeAdmin(admin.ModelAdmin):
    # add many2many relation field into list
    inlines = (LogInline,)

    # show below data in user challenge list
    list_display = ('user', 'challenge', 'is_active', 'start_date')

    # add filter for user
    list_filter = ('user',)


class LogAdmin(admin.ModelAdmin):

    # show below data in logs list
    list_display = ('user_challenge', 'date', 'points')


admin.site.register(Profile)
admin.site.register(UserChallenge, UserChallengeAdmin)
admin.site.register(Log, LogAdmin)