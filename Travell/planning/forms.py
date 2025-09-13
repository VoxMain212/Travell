from django import forms


class DateInput(forms.widgets.DateInput):
    input_type = 'date'


class TravelForm(forms.Form):
    title = forms.CharField(max_length=150, label="Название")
    destination = forms.CharField(max_length=150, label="Пункт назначения")
    date_in = forms.DateField(label="Дата отлета", widget=DateInput)
    date_out = forms.DateField(label="Дата прилета", widget=DateInput)
    price = forms.FloatField(label="Цена")
