import json
import time
from pathlib import Path
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from cms.defaults import DEFAULT_SITE_CONTENT
from cms.services import build_site_payload
from cms.models import ContactPage


SPA_TEMPLATE_CANDIDATES = ("index.html",)
CONTACT_THROTTLE_LIMIT = 5
CONTACT_THROTTLE_WINDOW_SECONDS = 600
HONEYPOT_FIELD = "website"
FAVICON_CANDIDATES = ("favicon.ico", "favicon.svg")


def _trimmed_value(payload, field_name):
    return str(payload.get(field_name, "")).strip()


def _client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _throttle_submission(request):
    now = int(time.time())
    history = request.session.get("contact_submission_history", [])
    history = [timestamp for timestamp in history if now - timestamp < CONTACT_THROTTLE_WINDOW_SECONDS]

    if len(history) >= CONTACT_THROTTLE_LIMIT:
        request.session["contact_submission_history"] = history
        request.session.modified = True
        return True

    history.append(now)
    request.session["contact_submission_history"] = history
    request.session.modified = True
    return False


def _build_formsubmit_payload(contact_page, payload, request):
    full_name = _trimmed_value(payload, "full_name")
    email = _trimmed_value(payload, "email")
    phone = _trimmed_value(payload, "phone")
    company = _trimmed_value(payload, "company")
    message = _trimmed_value(payload, "message")
    client_ip = _client_ip(request) or "Unknown"

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company": company,
        "message": message,
        "_subject": contact_page.form_subject or "New Contact Us Query - Leon & Walker",
        "_template": "table",
        "_captcha": "false",
        "_replyto": email,
        "submitted_from": request.build_absolute_uri("/contact"),
        "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "client_ip": client_ip,
    }


def _forward_contact_submission(contact_page, payload, request):
    encoded_payload = urllib_parse.urlencode(_build_formsubmit_payload(contact_page, payload, request)).encode("utf-8")
    outbound_request = urllib_request.Request(
        contact_page.form_action,
        data=encoded_payload,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    with urllib_request.urlopen(outbound_request, timeout=15) as response:
        response.read()


def _get_contact_page_for_submission():
    contact_page = ContactPage.objects.filter(pk=1).first()
    if contact_page:
        return contact_page
    return ContactPage(**DEFAULT_SITE_CONTENT["contact_page"])


@require_GET
def site_content_api(request):
    return JsonResponse(build_site_payload())


@require_GET
def health_api(request):
    frontend_template_exists = any(
        (Path(settings.FRONTEND_DIST_DIR) / candidate).exists() for candidate in SPA_TEMPLATE_CANDIDATES
    )
    database_ok = True
    database_error = ""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except OperationalError as exc:
        database_ok = False
        database_error = str(exc)

    return JsonResponse(
        {
            "ok": True,
            "service": "backend",
            "frontendTemplateAvailable": frontend_template_exists,
            "database": {
                "ok": database_ok,
                "engine": settings.DATABASES["default"]["ENGINE"],
                "error": database_error,
            },
        }
    )


@require_POST
@csrf_exempt
def contact_submission_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "message": "Invalid request payload."}, status=400)

    if _trimmed_value(payload, HONEYPOT_FIELD):
        return JsonResponse({"ok": True, "message": "Thanks for reaching out."})

    required_fields = {
        "full_name": "Full name is required.",
        "email": "Email is required.",
        "message": "Project details are required.",
    }
    for field_name, error_message in required_fields.items():
        if not _trimmed_value(payload, field_name):
            return JsonResponse({"ok": False, "message": error_message}, status=400)

    if _throttle_submission(request):
        return JsonResponse(
            {"ok": False, "message": "Too many messages sent recently. Please wait a few minutes and try again."},
            status=429,
        )

    contact_page = _get_contact_page_for_submission()
    if not contact_page.form_action:
        return JsonResponse({"ok": False, "message": "Contact form destination is not configured."}, status=503)

    try:
        _forward_contact_submission(contact_page, payload, request)
    except urllib_error.URLError:
        return JsonResponse(
            {"ok": False, "message": "We could not send your message right now. Please try again shortly."},
            status=502,
        )

    return JsonResponse({"ok": True, "message": "Your message has been sent successfully."})


@require_GET
@ensure_csrf_cookie
def spa_entry(request):
    for candidate in SPA_TEMPLATE_CANDIDATES:
        try:
            get_template(candidate)
        except Exception:
            continue
        return render(request, candidate)

    return HttpResponse(
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Leon & Walker Backend</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 0; padding: 32px; background: #0f172a; color: #e2e8f0; }
              .card { max-width: 720px; margin: 0 auto; padding: 24px; border-radius: 16px; background: #111827; }
              h1 { margin-top: 0; font-size: 28px; }
              p, li { line-height: 1.6; }
              code { background: #1f2937; padding: 2px 6px; border-radius: 6px; }
              a { color: #93c5fd; }
            </style>
          </head>
          <body>
            <main class="card">
              <h1>Leon & Walker Backend is running</h1>
              <p>The frontend build is not available in this deployment, so the backend served this fallback page instead of failing.</p>
              <p>Useful endpoints:</p>
              <ul>
                <li><a href="/api/health/"><code>/api/health/</code></a></li>
                <li><a href="/api/site-content/"><code>/api/site-content/</code></a></li>
                <li><code>/api/contact/</code></li>
                <li><a href="/admin/"><code>/admin/</code></a></li>
              </ul>
            </main>
          </body>
        </html>
        """,
        content_type="text/html; charset=utf-8",
    )


@require_GET
def favicon(request):
    for candidate in FAVICON_CANDIDATES:
        favicon_path = Path(settings.FRONTEND_DIST_DIR) / candidate
        if favicon_path.exists():
            response = FileResponse(favicon_path.open("rb"))
            if favicon_path.suffix == ".svg":
                response["Content-Type"] = "image/svg+xml"
            elif favicon_path.suffix == ".ico":
                response["Content-Type"] = "image/x-icon"
            return response

    return HttpResponse(status=204)
