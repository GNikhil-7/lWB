from django.core.management.base import BaseCommand

from cms.services import seed_site_content


class Command(BaseCommand):
    help = "Seed the CMS with default Leon & Walker content."

    def handle(self, *args, **options):
        seed_site_content()
        self.stdout.write(self.style.SUCCESS("CMS content seeded successfully."))
