from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote, name='random_quote'),
    path('top/', views.top_quotes, name='top_quotes'),
]
