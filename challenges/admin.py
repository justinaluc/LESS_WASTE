from django.contrib import admin

from .models import Challenge, Category, CategoryChallenge


class CategoryChallengeInline(admin.TabularInline):
    model = CategoryChallenge
    extra = 1


class ChallengeAdmin(admin.ModelAdmin):
    # add many2many relation field into list
    inlines = (CategoryChallengeInline,)

    # show below data in challenge list
    list_display = ("name", "duration", "frequency", "points")

    # add filters for frequency and points
    list_filter = ("frequency", "points")

    # sort list alphabetically by 'name'
    ordering = ("name",)


class CategoryAdmin(admin.ModelAdmin):
    # add many2many relation field into list
    inlines = (CategoryChallengeInline,)
    ordering = ("name",)


class CategoryChallengeAdmin(admin.ModelAdmin):
    # show below data in category challenge list
    list_display = ("category", "challenge")

    # add filter for category
    list_filter = ("category",)


admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryChallenge, CategoryChallengeAdmin)
