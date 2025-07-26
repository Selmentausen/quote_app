from django import forms
from .models import Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')
        if source and Quote.objects.filter(source=source).count() >= 3:
            raise forms.ValidationError('Cannot add more than three quotes from the same source.')
        return cleaned_data
