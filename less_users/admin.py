from django.contrib import admin

from .models import Profile, UserChallenge, Log


class LogInline(admin.TabularInline):
    model = Log
    extra = 1
    readonly_fields = ["date", "points"]


class LogAdmin(admin.ModelAdmin):
    # show below data in logs list
    list_display = ("user_challenge", "date", "points")


class UserChallengeAdmin(admin.ModelAdmin):
    # add many2many relation field into list
    inlines = (LogInline,)

    # show below data in user challenge list
    list_display = ("user", "challenge", "is_active", "is_deleted", "start_date")
    readonly_fields = ["user", "challenge", "start_date"]
    # add filter for user
    list_filter = ("user",)


class ProfileAdmin(admin.ModelAdmin):
    # add django-nested-admin into profile view (user/ user_challenge/ logs)

    # show below data in profile list
    list_display = ("user", "points")

    readonly_fields = ["user", "points"]


admin.site.register(Profile, ProfileAdmin)
admin.site.register(UserChallenge, UserChallengeAdmin)
admin.site.register(Log, LogAdmin)
