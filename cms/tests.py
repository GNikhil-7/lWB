import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from cms.models import AuditLog, HomeFeature, HomePage, SiteSettings
from cms.services import seed_site_content


class SiteContentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        temp_root = Path(__file__).resolve().parent.parent / ".tmp_test_media"
        temp_root.mkdir(exist_ok=True)
        cls._temp_media_dir = tempfile.mkdtemp(prefix="lw-web-test-media-", dir=temp_root)
        cls._overrides = override_settings(MEDIA_ROOT=cls._temp_media_dir)
        cls._overrides.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        try:
            super().tearDownClass()
        finally:
            cls._overrides.disable()
            shutil.rmtree(cls._temp_media_dir, ignore_errors=True)

    def test_seed_site_content_creates_default_records(self):
        seed_site_content()

        self.assertTrue(SiteSettings.objects.exists())
        self.assertTrue(HomePage.objects.exists())
        self.assertGreaterEqual(HomeFeature.objects.count(), 1)

    def test_api_returns_expected_shape(self):
        response = self.client.get(reverse("site-content-api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("home", payload)
        self.assertIn("about", payload)
        self.assertIn("services", payload)
        self.assertIn("contact", payload)
        self.assertIn("siteSettings", payload)
        self.assertGreaterEqual(len(payload["home"]["features"]), 1)
        self.assertIn("joinButtonUrl", payload["siteSettings"])
        self.assertIn("facebookUrl", payload["siteSettings"])
        self.assertIn("linkedinUrl", payload["siteSettings"])

    def test_api_read_does_not_seed_database_records(self):
        self.assertFalse(SiteSettings.objects.exists())
        self.assertFalse(HomePage.objects.exists())
        self.assertEqual(HomeFeature.objects.count(), 0)

        response = self.client.get(reverse("site-content-api"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(SiteSettings.objects.exists())
        self.assertFalse(HomePage.objects.exists())
        self.assertEqual(HomeFeature.objects.count(), 0)

    def test_api_returns_configurable_social_and_join_links(self):
        settings = SiteSettings.load()
        settings.join_button_label = "Apply Now"
        settings.join_button_url = "https://example.com/join"
        settings.facebook_url = "https://facebook.com/example"
        settings.linkedin_url = "https://linkedin.com/company/example"
        settings.save()

        response = self.client.get(reverse("site-content-api"))
        payload = response.json()

        self.assertEqual(payload["siteSettings"]["joinButtonLabel"], "Apply Now")
        self.assertEqual(payload["siteSettings"]["joinButtonUrl"], "https://example.com/join")
        self.assertEqual(payload["siteSettings"]["facebookUrl"], "https://facebook.com/example")
        self.assertEqual(payload["siteSettings"]["linkedinUrl"], "https://linkedin.com/company/example")

    def test_spa_entry_renders_built_index_template(self):
        temp_templates_root = Path(__file__).resolve().parent.parent / ".tmp_test_templates"
        temp_templates_root.mkdir(exist_ok=True)
        temp_template_dir = temp_templates_root / "spa-template"
        temp_template_dir.mkdir(exist_ok=True)
        try:
            (temp_template_dir / "index.html").write_text("<!doctype html><html><body><div id=\"root\"></div></body></html>", encoding="utf-8")
            with override_settings(
                TEMPLATES=[
                    {
                        "BACKEND": "django.template.backends.django.DjangoTemplates",
                        "DIRS": [temp_template_dir],
                        "APP_DIRS": True,
                        "OPTIONS": {
                            "context_processors": [
                                "django.template.context_processors.request",
                                "django.contrib.auth.context_processors.auth",
                                "django.contrib.messages.context_processors.messages",
                            ],
                        },
                    }
                ]
            ):
                response = self.client.get(reverse("spa-home"))
        finally:
            shutil.rmtree(temp_template_dir, ignore_errors=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div id="root"></div>', html=False)

    def test_spa_entry_falls_back_when_frontend_template_is_unavailable(self):
        with override_settings(
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [settings.BASE_DIR / "missing-frontend-dist"],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                }
            ]
        ):
            response = self.client.get(reverse("spa-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leon & Walker Backend is running", html=False)
        self.assertContains(response, "/api/health/", html=False)

    def test_health_api_reports_service_status(self):
        response = self.client.get(reverse("health-api"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["service"], "backend")
        self.assertIn("frontendTemplateAvailable", payload)
        self.assertTrue(payload["database"]["ok"])
        self.assertIn("engine", payload["database"])

    def test_admin_static_assets_are_served_locally(self):
        response = self.client.get("/static/admin/js/theme.js")

        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response["Content-Type"])

    def test_admin_login_works_with_cookie_sessions(self):
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        user_model.objects.create_superuser("admin", "admin@example.com", "test-pass-123")

        with override_settings(
            SESSION_ENGINE="django.contrib.sessions.backends.signed_cookies",
            MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage",
        ):
            response = self.client.post(
                reverse("admin:login"),
                data={
                    "username": "admin",
                    "password": "test-pass-123",
                    "next": "/admin/",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/admin/")

    def test_admin_login_uses_browser_safe_local_session_cookie_defaults(self):
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        user_model.objects.create_superuser("localadmin", "localadmin@example.com", "test-pass-456")

        response = self.client.post(
            reverse("admin:login"),
            data={
                "username": "localadmin",
                "password": "test-pass-456",
                "next": "/admin/",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies["sessionid"]["samesite"], "Lax")
        self.assertEqual(response.cookies["sessionid"]["secure"], "")

    def test_seed_command_runs(self):
        call_command("seed_cms")
        self.assertTrue(SiteSettings.objects.exists())

    def test_uploaded_image_is_preferred_in_api(self):
        seed_site_content()
        feature = HomeFeature.objects.first()
        feature.uploaded_image = "cms/feature.svg"
        feature.save(update_fields=["uploaded_image"])

        response = self.client.get(reverse("site-content-api"))
        payload = response.json()

        self.assertTrue(payload["home"]["features"][0]["imagePath"].startswith("/media/cms/"))

    def test_audit_log_handles_empty_file_fields(self):
        feature = HomeFeature.objects.create(
            title="Regression check",
            description="No uploaded file attached",
            image_path="/assets/img/test.svg",
            variant="dark",
            display_order=99,
        )

        log = AuditLog.objects.filter(object_id=str(feature.pk), action="create").first()

        self.assertIsNotNone(log)
        self.assertNotIn("uploaded_image", log.changes)

    @patch("cms.views.urllib_request.urlopen")
    def test_contact_submission_uses_internal_api_without_exposing_email(self, mock_urlopen):
        response = self.client.get(reverse("site-content-api"))
        payload = response.json()

        self.assertEqual(payload["contact"]["formAction"], "/api/contact/")

        mock_urlopen.return_value.__enter__.return_value.read.return_value = b"{}"
        submit_response = self.client.post(
            reverse("contact-submission-api"),
            data='{"full_name":"Nikhil","email":"test@example.com","phone":"9999999999","company":"Confluxaa","message":"Need help"}',
            content_type="application/json",
        )

        self.assertEqual(submit_response.status_code, 200)
        self.assertTrue(submit_response.json()["ok"])
        self.assertTrue(mock_urlopen.called)

    @patch("cms.views.urllib_request.urlopen")
    def test_contact_submission_blocks_honeypot_bots(self, mock_urlopen):
        response = self.client.post(
            reverse("contact-submission-api"),
            data='{"full_name":"Bot","email":"bot@example.com","message":"Spam","website":"https://spam.test"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(mock_urlopen.called)
