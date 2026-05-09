import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"


# ---------------------------------------------------------------------------
# Helpers — called before any setting reads os.environ
# ---------------------------------------------------------------------------

def _load_dotenv() -> None:
    """Parse backend/.env and inject values into os.environ via setdefault."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _env_flag(name: str, default: bool = False) -> bool:
    """Return a boolean from an environment variable string."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str) -> list[str]:
    """Return a list of non-empty strings split by comma from an env variable."""
    value = os.getenv(name, "")
    return [item.strip() for item in value.split(",") if item.strip()]


_load_dotenv()


# ---------------------------------------------------------------------------
# Environment detection  (private — not real Django settings)
# ---------------------------------------------------------------------------

_vercel_env: bool = (os.getenv("VERCEL_ENV") or "").strip().lower() in {
    "production", "preview", "development"
}
_railway_env: bool = bool(
    os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID")
)
_is_managed: bool = _vercel_env or _railway_env  # True on any cloud platform

# Public flag — available as settings.IS_MANAGED in urls.py / views
IS_MANAGED: bool = _is_managed


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG: bool = _env_flag("DJANGO_DEBUG", default=not _is_managed)

SECRET_KEY: str = os.getenv(
    "DJANGO_SECRET_KEY", "django-insecure-local-cms-secret-key"
)
if _is_managed and (
    not SECRET_KEY or SECRET_KEY.startswith("django-insecure-")
):
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be a strong random value in production. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(50))\""
    )

_force_secure_cookies: bool = _env_flag("FORCE_SECURE_COOKIES", default=False)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

_default_sqlite_url = f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}"
_raw_db_url = (os.getenv("DATABASE_URL") or "").strip()

# Reject obviously malformed URLs (common copy-paste mistakes)
if _raw_db_url and any(
    m in _raw_db_url for m in ("[", "]", "mailto:", "://http", "://https")
):
    raise ValueError(
        "Invalid DATABASE_URL. Use a plain PostgreSQL URL, e.g.: "
        "'postgresql://user:password@host:5432/postgres?sslmode=require'. "
        "Do not paste markdown links, brackets, or mailto-formatted text."
    )

# Cloud environments must have a real database URL
if _is_managed and not _raw_db_url:
    raise ImproperlyConfigured(
        "DATABASE_URL is not set. Add your Supabase PostgreSQL connection "
        "string to the environment variables in Vercel / Railway."
    )

# Vercel cannot reach Supabase direct hosts — they resolve to IPv6
if _vercel_env and "@db." in _raw_db_url and ".supabase.co" in _raw_db_url:
    raise ImproperlyConfigured(
        "Vercel cannot reliably reach Supabase direct database hosts (IPv6). "
        "Use the Session pooler URL from Supabase Dashboard > Connect "
        "(host: aws-0-<region>.pooler.supabase.com, port: 5432)."
    )

_database_url = _raw_db_url or _default_sqlite_url
_is_postgres = _database_url.split(":", 1)[0].lower() in {
    "postgres", "postgresql", "pgsql", "postgis"
}
_conn_max_age = int(os.getenv("DB_CONN_MAX_AGE", "0"))

DATABASES = {
    "default": dj_database_url.config(
        default=_database_url,
        conn_max_age=_conn_max_age,
        conn_health_checks=_conn_max_age > 0,
        ssl_require=_env_flag("DB_SSL_REQUIRE", default=_is_managed) and _is_postgres,
    )
}


# ---------------------------------------------------------------------------
# Hosts & CORS
# ---------------------------------------------------------------------------

ALLOWED_HOSTS: list[str] = ["127.0.0.1", "localhost", "0.0.0.0"]

if _is_managed:
    ALLOWED_HOSTS.append(".railway.app")
    ALLOWED_HOSTS.append(".vercel.app")

_vercel_host = os.getenv("VERCEL_URL", "").strip()
if _vercel_host:
    ALLOWED_HOSTS.append(_vercel_host)

_railway_host = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_host:
    ALLOWED_HOSTS.append(_railway_host)

# Add any custom hosts from env
ALLOWED_HOSTS.extend(_env_list("DJANGO_ALLOWED_HOSTS"))

# Cleanup duplicates
ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS))

CORS_ALLOWED_ORIGINS: list[str] = list(dict.fromkeys(_env_list("CORS_ALLOWED_ORIGINS")))
CORS_ALLOW_CREDENTIALS: bool = True

CSRF_TRUSTED_ORIGINS: list[str] = []
if _vercel_env:
    CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")
if _vercel_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_vercel_host}")
if _railway_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_host}")
CSRF_TRUSTED_ORIGINS.extend(_env_list("DJANGO_CSRF_TRUSTED_ORIGINS"))
CSRF_TRUSTED_ORIGINS.extend(CORS_ALLOWED_ORIGINS)
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

# Only trust forwarded headers behind a real reverse proxy (cloud only)
if _is_managed:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

    # HSTS — tell browsers to always use HTTPS (1 year, includes subdomains + preload list)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Vercel and Railway handle HTTPS at their edge — let them redirect, not Django.
# Setting this True would cause a redirect loop behind those platforms.
SECURE_SSL_REDIRECT = False


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "cms.middleware.CurrentUserAuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [FRONTEND_DIST_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Auth & Sessions
# ---------------------------------------------------------------------------

# Full password validation in production; relaxed locally for quick iteration
AUTH_PASSWORD_VALIDATORS = (
    [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]
    if _is_managed
    else []
)

SESSION_COOKIE_SECURE: bool = _is_managed or _force_secure_cookies
SESSION_COOKIE_SAMESITE: str = "Lax"
SESSION_COOKIE_AGE: int = 60 * 60 * 24 * 7  # 1 week

CSRF_COOKIE_SECURE: bool = _is_managed or _force_secure_cookies
CSRF_COOKIE_SAMESITE: str = "Lax"


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static & Media files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: compressed + hashed static files with long-lived cache headers.
# Use the manifest storage only in production where collectstatic has been run.
# Locally, use the plain backend to avoid StaticFilesStorage manifest errors.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if _is_managed
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
