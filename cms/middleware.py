from cms.audit import clear_current_user, set_current_user


class CurrentUserAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        set_current_user(user if getattr(user, "is_authenticated", False) else None)
        try:
            return self.get_response(request)
        finally:
            clear_current_user()
