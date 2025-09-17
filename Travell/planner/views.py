from django.shortcuts import render
from .forms import TripForm


COUNTRIES = {
    "japan": "Япония",
    "italy": "Италия",
    "thailand": "Таиланд",
    "iceland": "Исландия",
    "mexico": "Мексика",
    "new-zealand": "Новая Зеландия",
    "egypt": "Египет",
    "brazil": "Бразилия",
    "greece": "Греция",
    "switzerland": "Швейцария",
}

created_trips = [
{
                'title': 'Мечтаю в Токио',
                'discription': 'Хочу увидеть сакуру, попробовать рамен и прокатиться на синкансэне.',
                'country': 'Япония',
                'date_in': '15.04.2025',
                'date_out': '25.04.2025',
                'price': 2500
            },
            {
                'title': 'Альпы и шоколад',
                'discription': 'Горнолыжный отдых, сырные фондю и поезд Jungfraubahn.',
                'country': 'Швейцария',
                'date_in': '01.12.2025',
                'date_out': '10.12.2025',
                'price': 3200
            }
]

# Create your views here.
def index(req):
    print(req.COOKIES)
    theme = req.COOKIES.get('theme', 'light')

    resp = render(req, 'index.html', {'theme': theme})

    if 'theme' not in req.COOKIES:
        resp.set_cookie(
            'theme',
            'light',
            max_age=365 * 24 * 60 * 60,  # 1 год
            samesite='Lax'
        )
    return resp


def planner(req):
    theme = req.COOKIES.get('theme', 'light')

    resp = render(req, 'planner.html', {'countries': COUNTRIES.items(), 'trips': created_trips, 'theme': theme})

    if 'theme' not in req.COOKIES:
        resp.set_cookie(
            'theme',
            'light',
            max_age=365 * 24 * 60 * 60,  # 1 год
            samesite='Lax'
        )

    if req.method == "POST":
        form = TripForm(req.POST)
        if form.is_valid():
            data = form.cleaned_data
            cleaned_data = {
                'title': data['title'],
                'discription': data['discription'],
                'country': data['country'],
                'date_in': data['date_in'].strftime('%d.%m.%Y'),
                'date_out': data['date_out'].strftime('%d.%m.%Y'),
                'price': data['price']
            }
            created_trips.append(cleaned_data)
            print(created_trips)
    return resp
