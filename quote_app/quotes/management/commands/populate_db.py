from django.core.management.base import BaseCommand
from django.conf import settings
from quotes.models import Source, Quote, ViewCounter

import os
import json


class Command(BaseCommand):
    help = "Populates teh database with sample quotes and sources"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true',
                            help="Clear existing quotes, sources and view counter before populating")

    def handle(self, *args, **options):
        if options['clear']:
            Quote.objects.all().delete()
            Source.objects.all().delete()
            ViewCounter.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Cleared existing data"))

        self.stdout.write(self.style.SUCCESS("Populating database..."))

        if not ViewCounter.objects.exists():
            ViewCounter.objects.create(views=0)
            self.stdout.write(self.style.SUCCESS("Created new view counter"))

        json_path = os.path.join(settings.BASE_DIR, 'quotes', 'quotes.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("quotes.json not found"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON format in quotes.json"))
            return

        for entry in sample_data:
            source_name = entry.get('source')
            quotes = entry.get('quotes', [])
            if not source_name:
                self.stdout.write(self.style.ERROR("Skipping entry with missing source"))
                continue

            source, created = Source.objects.get_or_create(name=source_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created source: {source_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Source already exists: {source_name}'))

            existing_quotes = Quote.objects.filter(source=source).count()
            quotes_to_add = quotes[:3 - existing_quotes]
            for quote_data in quotes_to_add:
                text = quote_data.get('text')
                weight = quote_data.get('weight', 1)
                if not text:
                    self.stdout.write(self.style.WARNING(f'Skipping quote with missing text in {source_name}'))
                    continue
                if not Quote.objects.filter(text=text).exists():
                    try:
                        Quote.objects.create(text=text, source=source, weight=weight)
                        self.stdout.write(self.style.SUCCESS(f'Added quote: "{text}" to {source_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Failed to add quote: "{text}" to {source_name}: {str(e)}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Quote already exists: {text}'))

        self.stdout.write(self.style.SUCCESS("Database population complete!"))
