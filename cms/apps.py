from django.apps import AppConfig


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms"

    def ready(self):
        self._patch_broken_django_context_copy()
        import cms.signals  # noqa: F401

    @staticmethod
    def _patch_broken_django_context_copy():
        """
        Some Python 3.14 user-site Django installs in this environment ship a
        broken BaseContext.__copy__ implementation (`copy(super())`) that
        crashes every admin changelist render. Patch it back to Django's
        expected behavior at startup so the app runs correctly regardless of
        interpreter location.
        """
        from copy import copy

        from django.template.context import BaseContext

        def safe_base_context_copy(self):
            duplicate = BaseContext()
            duplicate.__class__ = self.__class__
            duplicate.__dict__ = copy(self.__dict__)
            duplicate.dicts = self.dicts[:]
            return duplicate

        BaseContext.__copy__ = safe_base_context_copy
