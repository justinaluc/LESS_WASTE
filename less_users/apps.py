from django.apps import AppConfig


class LessUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "less_users"

    def ready(self):
        import less_users.signals
