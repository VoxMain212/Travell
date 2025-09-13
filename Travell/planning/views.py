from django.shortcuts import render, HttpResponse
from .forms import TravelForm
import datetime


data = [
    {'title': 'title', 'destination': 'dest', 'date_in': datetime.date(2022, 12, 12), 'date_out': datetime.date(2022, 12, 12), 'price': 1390429.0}
]


# Create your views here.
def index(req):
    print(data)
    if req.method == "POST":
        form = TravelForm(req.POST)
        if form.is_valid():
            data.append(form.cleaned_data)
        new_form = TravelForm()
        return render(req, 'index.html', {'form': new_form, 'travels': data})
    else:
        form = TravelForm()
        return render(req, 'index.html', {'form': form, 'travels': data})
