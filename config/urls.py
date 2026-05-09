from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path
from django.views.static import serve

from cms.views import contact_submission_api, favicon, health_api, site_content_api, spa_entry


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_api, name="health-api"),
    path("api/site-content/", site_content_api, name="site-content-api"),
    path("api/contact/", contact_submission_api, name="contact-submission-api"),
    path("favicon.ico", favicon, name="favicon"),
    path("favicon.svg", serve, {"path": "favicon.svg", "document_root": settings.FRONTEND_DIST_DIR}),
    re_path(r"^(?:about|services|contact)(?:\.html)?/?$", spa_entry, name="spa-route"),
    path("", spa_entry, name="spa-home"),
]

# Local development only — serve frontend assets and media from the filesystem.
# On Vercel/Railway, static files are handled by WhiteNoise and media by cloud storage.
if not settings.IS_MANAGED:
    urlpatterns += [
        re_path(
            r"^assets/(?P<path>.*)$",
            serve,
            {"document_root": settings.FRONTEND_DIST_DIR / "assets"},
        ),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
