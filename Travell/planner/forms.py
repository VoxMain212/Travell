from django import forms


class TripForm(forms.Form):
    title = forms.CharField(max_length=150)
    discription = forms.CharField()
    country = forms.CharField(max_length=150)
    date_in = forms.DateField()
    date_out = forms.DateField()
    export = forms.CharField()
    price = forms.IntegerField()


class resultForm(forms.Form):
    search = forms.CharField()
    result_type = forms.CharField()


class FileForm(forms.Form):
    file = forms.FileField()