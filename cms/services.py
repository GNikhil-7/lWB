from cms.defaults import DEFAULT_SITE_CONTENT
from cms.models import (
    AboutPage,
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


def _image_url(obj):
    if getattr(obj, "uploaded_image", None):
        return obj.uploaded_image.url
    return obj.image_path


def _singleton_or_defaults(model, defaults):
    instance = model.objects.filter(pk=1).first()
    if not instance:
        return defaults.copy()

    data = defaults.copy()
    for field in defaults:
        value = getattr(instance, field, "")
        if value:
            data[field] = value
    return data


def _ordered_items_or_defaults(model, defaults):
    items = list(model.objects.all())
    if items:
        return items
    return defaults


def _apply_defaults(instance, defaults):
    changed = False
    for field, value in defaults.items():
        if not getattr(instance, field):
            setattr(instance, field, value)
            changed = True
    if changed:
        instance.save()


def _sync_ordered_items(model, items, unique_field="title"):
    if model.objects.exists():
        return

    for item in items:
        model.objects.create(**item)


def seed_site_content():
    _apply_defaults(SiteSettings.load(), DEFAULT_SITE_CONTENT["site_settings"])
    _apply_defaults(HomePage.load(), DEFAULT_SITE_CONTENT["home_page"])
    _apply_defaults(AboutPage.load(), DEFAULT_SITE_CONTENT["about_page"])
    _apply_defaults(ServicesPage.load(), DEFAULT_SITE_CONTENT["services_page"])
    _apply_defaults(ContactPage.load(), DEFAULT_SITE_CONTENT["contact_page"])

    _sync_ordered_items(HomeFeature, DEFAULT_SITE_CONTENT["home_features"])
    _sync_ordered_items(Founder, DEFAULT_SITE_CONTENT["founders"])
    _sync_ordered_items(ValueCard, DEFAULT_SITE_CONTENT["values"])
    _sync_ordered_items(ServiceCard, DEFAULT_SITE_CONTENT["service_cards"])
    _sync_ordered_items(IndustryCard, DEFAULT_SITE_CONTENT["industry_cards"])
    _sync_ordered_items(ResourceItem, DEFAULT_SITE_CONTENT["resource_items"])


def build_site_payload():
    site_settings = _singleton_or_defaults(SiteSettings, DEFAULT_SITE_CONTENT["site_settings"])
    home_page = _singleton_or_defaults(HomePage, DEFAULT_SITE_CONTENT["home_page"])
    about_page = _singleton_or_defaults(AboutPage, DEFAULT_SITE_CONTENT["about_page"])
    services_page = _singleton_or_defaults(ServicesPage, DEFAULT_SITE_CONTENT["services_page"])
    contact_page = _singleton_or_defaults(ContactPage, DEFAULT_SITE_CONTENT["contact_page"])
    home_features = _ordered_items_or_defaults(HomeFeature, DEFAULT_SITE_CONTENT["home_features"])
    founders = _ordered_items_or_defaults(Founder, DEFAULT_SITE_CONTENT["founders"])
    values = _ordered_items_or_defaults(ValueCard, DEFAULT_SITE_CONTENT["values"])
    service_cards = _ordered_items_or_defaults(ServiceCard, DEFAULT_SITE_CONTENT["service_cards"])
    industry_cards = _ordered_items_or_defaults(IndustryCard, DEFAULT_SITE_CONTENT["industry_cards"])
    resource_items = _ordered_items_or_defaults(ResourceItem, DEFAULT_SITE_CONTENT["resource_items"])

    return {
        "siteSettings": {
            "footerDescription": site_settings["footer_description"],
            "newsletterTitle": site_settings["newsletter_title"],
            "newsletterText": site_settings["newsletter_text"],
            "joinButtonLabel": site_settings["join_button_label"],
            "joinButtonUrl": site_settings["join_button_url"],
            "facebookUrl": site_settings["facebook_url"],
            "linkedinUrl": site_settings["linkedin_url"],
            "copyrightText": site_settings["copyright_text"],
            "developerName": site_settings["developer_name"],
            "developerUrl": site_settings["developer_url"],
        },
        "home": {
            "heroWatermark": home_page["hero_watermark"],
            "heroTitle": home_page["hero_title"],
            "heroSubtitle": home_page["hero_subtitle"],
            "heroKnowMoreLabel": home_page["hero_know_more_label"],
            "heroKnowMoreUrl": home_page["hero_know_more_url"],
            "introTitle": home_page["intro_title"],
            "introBody": home_page["intro_body"],
            "introKnowMoreLabel": home_page["intro_know_more_label"],
            "introKnowMoreUrl": home_page["intro_know_more_url"],
            "whyTitle": home_page["why_title"],
            "features": [
                {
                    "title": feature.title if hasattr(feature, "title") else feature["title"],
                    "description": feature.description if hasattr(feature, "description") else feature["description"],
                    "imagePath": _image_url(feature) if hasattr(feature, "_meta") else feature["image_path"],
                    "variant": feature.variant if hasattr(feature, "variant") else feature["variant"],
                    "knowMoreLabel": feature.know_more_label if hasattr(feature, "know_more_label") else feature.get("know_more_label", ""),
                    "knowMoreUrl": feature.know_more_url if hasattr(feature, "know_more_url") else feature.get("know_more_url", ""),
                }
                for feature in home_features
            ],
        },
        "about": {
            "heroTitle": about_page["hero_title"],
            "heroSubtitle": about_page["hero_subtitle"],
            "heroKnowMoreLabel": about_page["hero_know_more_label"],
            "heroKnowMoreUrl": about_page["hero_know_more_url"],
            "aboutTitle": about_page["about_title"],
            "aboutParagraphOne": about_page["about_paragraph_one"],
            "aboutParagraphTwo": about_page["about_paragraph_two"],
            "philosophyTitle": about_page["philosophy_title"],
            "philosophyBody": about_page["philosophy_body"],
            "foundersTitle": about_page["founders_title"],
            "foundersSubtitle": about_page["founders_subtitle"],
            "valuesTitle": about_page["values_title"],
            "founders": [
                {
                    "name": founder.name if hasattr(founder, "name") else founder["name"],
                    "role": founder.role if hasattr(founder, "role") else founder["role"],
                    "quote": founder.quote if hasattr(founder, "quote") else founder["quote"],
                    "bioPrimary": founder.bio_primary if hasattr(founder, "bio_primary") else founder["bio_primary"],
                    "bioSecondary": founder.bio_secondary if hasattr(founder, "bio_secondary") else founder.get("bio_secondary", ""),
                    "imagePath": _image_url(founder) if hasattr(founder, "_meta") else founder["image_path"],
                    "styleVariant": founder.style_variant if hasattr(founder, "style_variant") else founder["style_variant"],
                }
                for founder in founders
            ],
            "values": [
                {
                    "title": value.title if hasattr(value, "title") else value["title"],
                    "description": value.description if hasattr(value, "description") else value["description"],
                    "imagePath": _image_url(value) if hasattr(value, "_meta") else value["image_path"],
                    "styleVariant": value.style_variant if hasattr(value, "style_variant") else value["style_variant"],
                }
                for value in values
            ],
        },
        "services": {
            "heroTitle": services_page["hero_title"],
            "heroSubtitle": services_page["hero_subtitle"],
            "heroKnowMoreLabel": services_page["hero_know_more_label"],
            "heroKnowMoreUrl": services_page["hero_know_more_url"],
            "servicesTitle": services_page["services_title"],
            "industriesTitle": services_page["industries_title"],
            "cards": [
                {
                    "title": card.title if hasattr(card, "title") else card["title"],
                    "imagePath": _image_url(card) if hasattr(card, "_meta") else card["image_path"],
                    "knowMoreLabel": card.know_more_label if hasattr(card, "know_more_label") else card.get("know_more_label", ""),
                    "knowMoreUrl": card.know_more_url if hasattr(card, "know_more_url") else card.get("know_more_url", ""),
                }
                for card in service_cards
            ],
            "industries": [
                {
                    "title": card.title if hasattr(card, "title") else card["title"],
                    "imagePath": _image_url(card) if hasattr(card, "_meta") else card["image_path"],
                    "styleVariant": card.style_variant if hasattr(card, "style_variant") else card["style_variant"],
                }
                for card in industry_cards
            ],
            "resources": [
                {
                    "title": item.title if hasattr(item, "title") else item["title"],
                    "description": item.description if hasattr(item, "description") else item["description"],
                    "imagePath": _image_url(item) if hasattr(item, "_meta") else item["image_path"],
                    "knowMoreLabel": item.know_more_label if hasattr(item, "know_more_label") else item.get("know_more_label", ""),
                    "knowMoreUrl": item.know_more_url if hasattr(item, "know_more_url") else item.get("know_more_url", ""),
                }
                for item in resource_items
            ],
        },
        "contact": {
            "kicker": contact_page["kicker"],
            "title": contact_page["title"],
            "lead": contact_page["lead"],
            "informationTitle": contact_page["information_title"],
            "locationLabel": contact_page["location_label"],
            "locationValue": contact_page["location_value"],
            "emailLabel": contact_page["email_label"],
            "emailValue": contact_page["email_value"],
            "websiteLabel": contact_page["website_label"],
            "websiteValue": contact_page["website_value"],
            "formTitle": contact_page["form_title"],
            "formAction": "/api/contact/",
            "formSubject": contact_page["form_subject"],
        },
    }
