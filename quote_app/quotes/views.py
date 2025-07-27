import random

from django.db.models import F
from django.shortcuts import render, redirect

from .forms import QuoteForm
from .models import Quote, ViewCounter


# Create your views here.
def random_quote(request):
    # Increment view counter atomically
    ViewCounter.objects.update(views=F('views') + 1)
    view_counter = ViewCounter.objects.first()

    # Select random quote based on weight
    quotes = Quote.objects.all()
    if quotes.exists():
        selected_quote = random.choices(quotes, weights=[q.weight for q in quotes], k=1)[0]
    else:
        selected_quote = None

    # handling like/dislike
    voted_quotes = request.session.get('voted_quotes', {})
    if request.method == 'POST':
        quote_id = request.POST.get('quote_id')
        vote_type = request.POST.get('vote_type')
        if quote_id not in voted_quotes:
            if vote_type == 'like':
                Quote.objects.filter(id=quote_id).update(likes=F('likes') + 1)
            elif vote_type == 'dislike':
                Quote.objects.filter(id=quote_id).update(dislikes=F('dislikes') + 1)
            voted_quotes[quote_id] = vote_type
            request.session['voted_quotes'] = voted_quotes
        return redirect('random_quote')

    user_vote = voted_quotes.get(str(selected_quote.id), None) if selected_quote else None
    context = {
        "quote": selected_quote,
        "view_counter": view_counter,
        "user_vote": user_vote,
    }
    return render(request, 'quotes/random_quote.html', context)


def top_quotes(request):
    top_quotes = Quote.objects.order_by('-likes')[:10]
    context = {"top_quotes": top_quotes}
    return render(request, 'quotes/top_quotes.html', context)


def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.source = form.cleaned_data['source']
            quote.save()
            return redirect('random_quote')
    else:
        form = QuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})