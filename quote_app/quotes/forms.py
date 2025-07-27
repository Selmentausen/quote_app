from django import forms
from .models import Quote, Source


class QuoteForm(forms.ModelForm):
    source_name = forms.CharField(max_length=255, required=True, label="Source (e.g., Movie or Book Title)")

    class Meta:
        model = Quote
        fields = ['text', 'weight']

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        source = cleaned_data.get('source_name')

        # check for duplicate quotes
        if Quote.objects.filter(text=text).exists():
            raise forms.ValidationError("This quote already exists.")

        # check for quotes from same source not being more than 3
        source, _ = Source.objects.get_or_create(name=source.strip())
        if Quote.objects.filter(source=source).count() >= 3:
            raise forms.ValidationError('Cannot add more than three quotes from the same source.')

        cleaned_data['source'] = source
        return cleaned_data
