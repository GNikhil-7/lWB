import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cms", "0003_know_more_buttons"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("model_name", models.CharField(max_length=120)),
                ("object_id", models.CharField(max_length=64)),
                ("object_repr", models.CharField(max_length=255)),
                ("action", models.CharField(choices=[("create", "Created"), ("update", "Updated"), ("delete", "Deleted")], max_length=20)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("changes", models.JSONField(blank=True, default=dict)),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cms_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-changed_at", "-id"],
            },
        ),
    ]
