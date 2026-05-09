from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0002_image_upload_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="aboutpage",
            name="hero_know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="aboutpage",
            name="hero_know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homefeature",
            name="know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homefeature",
            name="know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="intro_know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="homepage",
            name="intro_know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="resourceitem",
            name="know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="resourceitem",
            name="know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="servicecard",
            name="know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="servicecard",
            name="know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="servicespage",
            name="hero_know_more_label",
            field=models.CharField(blank=True, default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="servicespage",
            name="hero_know_more_url",
            field=models.CharField(blank=True, default="", max_length=255),
            preserve_default=False,
        ),
    ]
