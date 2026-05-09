from django.contrib import admin
from django.utils.html import format_html

from cms.models import (
    AboutPage,
    AuditLog,
    ContactPage,
    Founder,
    HomeFeature,
    HomePage,
    IndustryCard,
    ResourceItem,
    ServiceCard,
    ServicesPage,
    SiteSettings,
    ValueCard,
)


def format_change_summary(changes):
    if not changes:
        return "No field changes recorded."

    lines = []
    for field_name, values in changes.items():
        previous = values.get("from", "")
        current = values.get("to", "")
        lines.append(
            format_html(
                "<div><strong>{}</strong>: <span style=\"color:#7a7a7a;\">{}</span> -> <span>{}</span></div>",
                field_name,
                previous or "(empty)",
                current or "(empty)",
            )
        )
    return format_html("".join(str(line) for line in lines))


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Footer Content", {"fields": ("footer_description", "newsletter_title", "newsletter_text")}),
        (
            "Header and Social Links",
            {
                "fields": ("join_button_label", "join_button_url", "facebook_url", "linkedin_url"),
                "description": "Controls the Join Now button and the Facebook/LinkedIn links shown in the header and footer.",
            },
        ),
        ("Credits", {"fields": ("copyright_text", "developer_name", "developer_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero Section", {"fields": ("hero_watermark", "hero_title", "hero_subtitle")}),
        (
            "Hero Know More Button",
            {
                "fields": ("hero_know_more_label", "hero_know_more_url"),
                "description": "Controls the Know More button in the Home page hero banner.",
            },
        ),
        ("Intro Section", {"fields": ("intro_title", "intro_body")}),
        (
            "Intro Know More Button",
            {
                "fields": ("intro_know_more_label", "intro_know_more_url"),
                "description": "Controls the Know More button in the Home page intro section.",
            },
        ),
        ("Why Section", {"fields": ("why_title",)}),
    )

    def has_add_permission(self, request):
        return not HomePage.objects.exists()


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero Section", {"fields": ("hero_title", "hero_subtitle")}),
        (
            "Hero Know More Button",
            {
                "fields": ("hero_know_more_label", "hero_know_more_url"),
                "description": "Controls the Know More button in the About page hero banner.",
            },
        ),
        ("About Section", {"fields": ("about_title", "about_paragraph_one", "about_paragraph_two")}),
        ("Philosophy Section", {"fields": ("philosophy_title", "philosophy_body")}),
        ("Founders Section", {"fields": ("founders_title", "founders_subtitle")}),
        ("Values Section", {"fields": ("values_title",)}),
    )

    def has_add_permission(self, request):
        return not AboutPage.objects.exists()


@admin.register(ServicesPage)
class ServicesPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero Section", {"fields": ("hero_title", "hero_subtitle")}),
        (
            "Hero Know More Button",
            {
                "fields": ("hero_know_more_label", "hero_know_more_url"),
                "description": "Controls the Know More button in the Services page hero banner.",
            },
        ),
        ("Section Headings", {"fields": ("services_title", "industries_title")}),
    )

    def has_add_permission(self, request):
        return not ServicesPage.objects.exists()


@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ContactPage.objects.exists()


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("changed_at", "model_name", "object_repr", "action", "actor_name")
    list_filter = ("action", "model_name", "changed_at")
    search_fields = ("model_name", "object_repr", "object_id", "changed_by__username", "changed_by__first_name", "changed_by__last_name")
    readonly_fields = ("model_name", "object_id", "object_repr", "action", "changed_by", "changed_at", "change_details")
    fields = ("changed_at", "changed_by", "model_name", "object_id", "object_repr", "action", "change_details")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def actor_name(self, obj):
        return obj.actor_label

    actor_name.short_description = "Changed by"

    def change_details(self, obj):
        return format_change_summary(obj.changes)

    change_details.short_description = "Field changes"


@admin.register(HomeFeature)
class HomeFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "variant", "button_location_display", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display", "button_location_display")
    fields = (
        "title",
        "description",
        "uploaded_image",
        "image_path",
        "image_preview_display",
        "variant",
        "button_location_display",
        "know_more_label",
        "know_more_url",
        "display_order",
    )

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"

    def button_location_display(self, obj):
        if not obj:
            return "Shown only for highlight cards after you save this feature"
        if obj.variant == "highlight":
            return "Home page -> Why Companies Work With Us -> highlighted card Know More button"
        return "No Know More button shown for dark variant cards"

    button_location_display.short_description = "Know More button location"


@admin.register(Founder)
class FounderAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "style_variant", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display",)
    fields = (
        "name",
        "role",
        "quote",
        "bio_primary",
        "bio_secondary",
        "uploaded_image",
        "image_path",
        "image_preview_display",
        "style_variant",
        "display_order",
    )

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"


@admin.register(ValueCard)
class ValueCardAdmin(admin.ModelAdmin):
    list_display = ("title", "style_variant", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display",)
    fields = ("title", "description", "uploaded_image", "image_path", "image_preview_display", "style_variant", "display_order")

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"


@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ("title", "button_location_display", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display", "button_location_display")
    fields = (
        "title",
        "uploaded_image",
        "image_path",
        "image_preview_display",
        "button_location_display",
        "know_more_label",
        "know_more_url",
        "display_order",
    )

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"

    def button_location_display(self, obj):
        return "Services page -> Services list card Know More button"

    button_location_display.short_description = "Know More button location"


@admin.register(IndustryCard)
class IndustryCardAdmin(admin.ModelAdmin):
    list_display = ("title", "style_variant", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display",)
    fields = ("title", "uploaded_image", "image_path", "image_preview_display", "style_variant", "display_order")

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"


@admin.register(ResourceItem)
class ResourceItemAdmin(admin.ModelAdmin):
    list_display = ("title", "button_location_display", "display_order")
    list_editable = ("display_order",)
    ordering = ("display_order", "id")
    readonly_fields = ("image_preview_display", "button_location_display")
    fields = (
        "title",
        "description",
        "uploaded_image",
        "image_path",
        "image_preview_display",
        "button_location_display",
        "know_more_label",
        "know_more_url",
        "display_order",
    )

    def image_preview_display(self, obj):
        if obj and getattr(obj, "uploaded_image", None):
            return format_html('<img src="{}" style="max-width: 220px; border-radius: 6px;" />', obj.uploaded_image.url)
        if obj and obj.image_path:
            return obj.image_path
        return "Upload image or use image path."

    image_preview_display.short_description = "Preview"

    def button_location_display(self, obj):
        return "Services page -> Resource section Know More button"

    button_location_display.short_description = "Know More button location"
