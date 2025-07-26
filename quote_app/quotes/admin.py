from django.contrib import admin
from .models import Source, Quote, ViewCounter
from .forms import QuoteForm


# Register your models here.
class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm
    list_dislpay = ('text', 'source', 'weight', 'likes', 'dislikes')


admin.site.register(Source)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(ViewCounter)
