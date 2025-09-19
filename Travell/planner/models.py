from django.db import models

# Create your models here.
class Trip(models.Model):
    title = models.CharField(verbose_name='Название', max_length=150)
    discription = models.TextField('Описание')
    country = models.CharField('Страна', max_length=150)
    date_in = models.CharField('Дата отлета')
    date_out = models.CharField('Дата прилета')
    price = models.IntegerField('Цена')