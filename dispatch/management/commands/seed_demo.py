from django.core.management.base import BaseCommand
from dispatch.demo_data import seed_demo_data


class Command(BaseCommand):
    help = "Seed demo mechanics, requests, offers, and chat messages."

    def handle(self, *args, **options):
        seed_demo_data()
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

