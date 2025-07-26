from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Quote(models.Model):
    text = models.TextField(unique=True)  # made unique to prevent duplicates
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text


class ViewCounter(models.Model):
    views = models.PositiveIntegerField(default=0)
