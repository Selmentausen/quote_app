from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.db.models import F

from .models import Source, Quote, ViewCounter
from .forms import QuoteForm


# Create your tests here.
class QuoteModelTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(name='Star Wars')
        self.quote = Quote.objects.create(
            text="May the Force be with you.",
            source=self.source,
            weight=5
        )
        self.view_counter = ViewCounter.objects.create(views=0)

    def test_quote_uniqueness(self):
        with self.assertRaises(IntegrityError):
            Quote.objects.create(
                text="May the Force be with you.",
                source=self.source,
                weight=5
            )

    def test_max_three_quotes_per_source(self):
        Quote.objects.create(text="Quote 2", source=self.source, weight=3)
        Quote.objects.create(text="Quote 3", source=self.source, weight=2)
        # Fourth quote should fail via form validation
        # Directly adding more than 3 quotes to the model is allowed
        Quote.objects.create(text="Quote 4", source=self.source, weight=1)

    def test_weight_validation(self):
        with self.assertRaises(ValidationError):
            quote = Quote(text="Invalid weight", source=self.source, weight=0)
            quote.full_clean()

    def test_view_counter_increment(self):
        self.view_counter.views = 5
        self.view_counter.save()
        ViewCounter.objects.update(views=F('views') + 1)
        self.view_counter.refresh_from_db()
        self.assertEqual(self.view_counter.views, 6)


class QuoteFormTest(TestCase):
    def setUp(self):
        self.source = Source.objects.create(name='Source 1')
        Quote.objects.create(text='Quote 1', source=self.source, weight=5)
        Quote.objects.create(text='Quote 2', source=self.source, weight=3)
        Quote.objects.create(text='Quote 3', source=self.source, weight=2)

    def test_valid_form(self):
        form_data = {'text': "Quote 4",
                     'source_name': "Source 2",
                     'weight': 4}
        form = QuoteForm(data=form_data)
        self.assertTrue(form.is_valid())
        quote = form.save(commit=False)
        quote.source = form.cleaned_data['source']
        quote.save()
        self.assertEqual(Quote.objects.count(), 4)

    def test_duplicate_quote(self):
        form_data = {'text': "Quote 1",
                     'source_name': "Source 1",
                     'weight': 4}
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Quote with this Text already exists.", form.errors['text'])

    def test_max_three_quotes_per_source(self):
        form_data = {'text': "Quote 5",
                     'source_name': "Source 1",
                     'weight': 1}
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Cannot add more than three quotes from the same source.", form.errors['__all__'])
