from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="founder",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
        migrations.AddField(
            model_name="homefeature",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
        migrations.AddField(
            model_name="industrycard",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
        migrations.AddField(
            model_name="resourceitem",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
        migrations.AddField(
            model_name="servicecard",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
        migrations.AddField(
            model_name="valuecard",
            name="uploaded_image",
            field=models.FileField(blank=True, upload_to="cms/"),
        ),
    ]
