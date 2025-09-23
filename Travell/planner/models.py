from django.db import models

# Create your models here.
class Trip(models.Model):
    id = models.CharField('id', primary_key=True, max_length=250)
    title = models.CharField(verbose_name='Название', max_length=150)
    discription = models.TextField('Описание', max_length=500)
    country = models.CharField('Страна', max_length=150)
    date_in = models.CharField('Дата отлета', max_length=12)
    date_out = models.CharField('Дата прилета', max_length=12)
    price = models.IntegerField('Цена')