from django import forms


class TripForm(forms.Form):
    title = forms.CharField(max_length=150)
    discription = forms.CharField()
    country = forms.CharField(max_length=150)
    date_in = forms.DateTimeField()
    date_out = forms.DateTimeField()
    price = forms.IntegerField()