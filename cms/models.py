from django.conf import settings
from django.db import models


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    footer_description = models.TextField(blank=True)
    newsletter_title = models.CharField(max_length=120, blank=True)
    newsletter_text = models.TextField(blank=True)
    join_button_label = models.CharField(max_length=80, blank=True)
    join_button_url = models.CharField(max_length=255, blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    copyright_text = models.CharField(max_length=255, blank=True)
    developer_name = models.CharField(max_length=120, blank=True)
    developer_url = models.URLField(blank=True)

    def __str__(self):
        return "Site Settings"


class HomePage(SingletonModel):
    hero_watermark = models.CharField(max_length=24, blank=True)
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_know_more_label = models.CharField(max_length=80, blank=True)
    hero_know_more_url = models.CharField(max_length=255, blank=True)
    intro_title = models.CharField(max_length=255, blank=True)
    intro_body = models.TextField(blank=True)
    intro_know_more_label = models.CharField(max_length=80, blank=True)
    intro_know_more_url = models.CharField(max_length=255, blank=True)
    why_title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "Home Page"


class HomeFeature(models.Model):
    VARIANT_CHOICES = [
        ("highlight", "Highlight"),
        ("dark", "Dark"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    variant = models.CharField(max_length=20, choices=VARIANT_CHOICES, default="dark")
    know_more_label = models.CharField(max_length=80, blank=True)
    know_more_url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class AboutPage(SingletonModel):
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_know_more_label = models.CharField(max_length=80, blank=True)
    hero_know_more_url = models.CharField(max_length=255, blank=True)
    about_title = models.CharField(max_length=255, blank=True)
    about_paragraph_one = models.TextField(blank=True)
    about_paragraph_two = models.TextField(blank=True)
    philosophy_title = models.CharField(max_length=255, blank=True)
    philosophy_body = models.TextField(blank=True)
    founders_title = models.CharField(max_length=255, blank=True)
    founders_subtitle = models.TextField(blank=True)
    values_title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "About Page"


class Founder(models.Model):
    STYLE_CHOICES = [
        ("primary", "Primary"),
        ("secondary", "Secondary"),
    ]

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    quote = models.TextField()
    bio_primary = models.TextField()
    bio_secondary = models.TextField(blank=True)
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    style_variant = models.CharField(max_length=20, choices=STYLE_CHOICES, default="primary")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class ValueCard(models.Model):
    STYLE_CHOICES = [
        ("primary", "Primary"),
        ("black", "Black"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    style_variant = models.CharField(max_length=20, choices=STYLE_CHOICES, default="primary")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class ServicesPage(SingletonModel):
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_know_more_label = models.CharField(max_length=80, blank=True)
    hero_know_more_url = models.CharField(max_length=255, blank=True)
    services_title = models.CharField(max_length=255, blank=True)
    industries_title = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "Services Page"


class ServiceCard(models.Model):
    title = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    know_more_label = models.CharField(max_length=80, blank=True)
    know_more_url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class IndustryCard(models.Model):
    STYLE_CHOICES = [
        ("primary", "Primary"),
        ("black", "Black"),
        ("outlined", "Outlined"),
    ]

    title = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    style_variant = models.CharField(max_length=20, choices=STYLE_CHOICES, default="primary")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class ResourceItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_path = models.CharField(max_length=255, blank=True)
    uploaded_image = models.FileField(upload_to="cms/", blank=True)
    know_more_label = models.CharField(max_length=80, blank=True)
    know_more_url = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class ContactPage(SingletonModel):
    kicker = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=255, blank=True)
    lead = models.TextField(blank=True)
    information_title = models.CharField(max_length=120, blank=True)
    location_label = models.CharField(max_length=80, blank=True)
    location_value = models.CharField(max_length=255, blank=True)
    email_label = models.CharField(max_length=80, blank=True)
    email_value = models.EmailField(blank=True)
    website_label = models.CharField(max_length=80, blank=True)
    website_value = models.URLField(blank=True)
    form_title = models.CharField(max_length=120, blank=True)
    form_action = models.URLField(blank=True)
    form_subject = models.CharField(max_length=255, blank=True)
    form_success_url = models.URLField(blank=True)

    def __str__(self):
        return "Contact Page"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
    ]

    model_name = models.CharField(max_length=120)
    object_id = models.CharField(max_length=64)
    object_repr = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_audit_logs",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-changed_at", "-id"]

    def __str__(self):
        return f"{self.model_name} {self.get_action_display()} by {self.actor_label}"

    @property
    def actor_label(self):
        if self.changed_by:
            full_name = self.changed_by.get_full_name().strip()
            if full_name:
                return full_name
            return self.changed_by.get_username()
        return "System"
