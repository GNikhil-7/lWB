from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0004_auditlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="facebook_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="join_button_url",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="linkedin_url",
            field=models.URLField(blank=True),
        ),
    ]
