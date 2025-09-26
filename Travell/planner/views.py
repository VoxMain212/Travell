from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from .forms import TripForm, FileForm, resultForm
from uuid import uuid4
import os
import json
from xml.dom.minidom import parseString
import dicttoxml
import xml.etree.ElementTree as ET
from .models import Trip


def xml_string_to_dict(xml_str):
    def etree_to_dict(t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = {}
            for dc in map(etree_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        if not isinstance(dd[k], list):
                            dd[k] = [dd[k]]
                        dd[k].append(v)
                    else:
                        dd[k] = v
            d = {t.tag: dd}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    root = ET.fromstring(xml_str)
    return etree_to_dict(root)


if not os.path.exists('travells'):
    os.mkdir('travells')

def dict_to_xml_string(data, root_tag='root', indent="  "):
    """
    Конвертирует словарь в красиво отформатированную XML-строку.
    """
    # Преобразуем словарь в XML (байты)
    xml_bytes = dicttoxml.dicttoxml(data, custom_root=root_tag, attr_type=False)
    
    # Парсим для красивого форматирования
    dom = parseString(xml_bytes)
    
    # Возвращаем как строку
    return dom.toprettyxml(indent=indent)

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

created_trips = {

}

def add_travell(travel_info: dict):
    if not('id' in travel_info.keys()):
        travel_info['id'] = uuid4().hex
    print(travel_info)
    with open(os.path.join('travells', uuid4().hex), 'w', encoding='utf-8') as f:
        json.dump(travel_info, f)
    created_trips.setdefault(travel_info['id'], travel_info)


def load_travells():
    if not os.path.exists('travells'):
        return
    for file in os.listdir('travells'):
        with open(os.path.join('travells', file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['id'] = file
        created_trips.setdefault(file, data)


load_travells()


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
    ret_trips = []
    ret_trips.extend(created_trips.values())
    ret_trips.extend(Trip.objects.all())

    if req.method == "POST":
        if 'title' in req.POST:
            form = TripForm(req.POST)
            if form.is_valid():
                data = form.cleaned_data
                f = 1
                for trip in created_trips.values():
                    f *= not data['title'] == trip['title']
                if f:
                    cleaned_data = {
                        'id': uuid4().hex,
                        'title': data['title'],
                        'discription': data['discription'],
                        'country': data['country'],
                        'date_in': data['date_in'].strftime('%d.%m.%Y'),
                        'date_out': data['date_out'].strftime('%d.%m.%Y'),
                        'price': int(data['price'])
                    }
                    created_trips.setdefault(cleaned_data['id'], cleaned_data)
                    if form.cleaned_data['export'] == 'json':
                        add_travell(cleaned_data)
                        http_response = HttpResponse(json.dumps(cleaned_data), content_type='application/json')
                        http_response['Content-Disposition'] = f'attachment; filename="new_travel.json"'
                        return http_response
                    elif form.cleaned_data['export'] == 'xml':
                        add_travell(cleaned_data)
                        http_response = HttpResponse(dict_to_xml_string(cleaned_data), content_type='application/xml')
                        http_response['Content-Disposition'] = f'attachment; filename="new_travel.xml"'
                        return http_response
                    elif form.cleaned_data['export'] == 'db':
                        if not Trip.objects.filter(title=form.cleaned_data['title']).exists():
                            print(cleaned_data)
                            trip = Trip(**cleaned_data)
                            trip.save()
        elif 'result_type' in req.POST:
            form = resultForm(req.POST)
            if form.is_valid():
                res_type = form.cleaned_data['result_type']
                if res_type == 'db':
                    db_trips = []
                    for trip in Trip.objects.all():
                        getted_trip = {
                            'id': trip.id,
                            'title': trip.title,
                            'discription': trip.discription,
                            'country': trip.country,
                            'date_in': trip.date_in,
                            'date_out': trip.date_out,
                            'price': int(trip.price)
                        }
                        db_trips.append(getted_trip)
                    ret_trips = db_trips
                elif res_type == 'json':
                    db_trips = []
                    for file in os.listdir('travells'):
                        with open(f'travells\\{file}', 'r', encoding='utf-8') as f:
                            trip = json.load(f)
                        db_trips.append(trip)
                    ret_trips = db_trips
    resp = render(req, 'planner.html', {'countries': COUNTRIES.items(), 'trips': ret_trips, 'theme': theme})

    if 'theme' not in req.COOKIES:
        resp.set_cookie(
            'theme',
            'light',
            max_age=365 * 24 * 60 * 60,  # 1 год
            samesite='Lax'
        )

    return resp


def exporter(req):
    if req.method == "POST":
        form = FileForm(req.POST, req.FILES)

        if form.is_valid():
            file = req.FILES['file']
            content = file.read()
            print(str(file))
            if str(file).endswith('.json'):
                data: dict = json.loads(content)
                fields = ['title', 'discription', 'country', 'date_in', 'date_out', 'price']
                f = 1
                for field in fields:
                    f *= field in data.keys()
                    if not f:
                        break
                if f:
                    g = 1
                    for travel in created_trips.values():
                        g *= not (data['title'] == travel['title'])
                    if g:
                        add_travell(data)
            elif str(file).endswith('.xml'):
                data = xml_string_to_dict(content)['root']
                fields = ['title', 'discription', 'country', 'date_in', 'date_out', 'price']
                f = 1
                for field in fields:
                    f *= field in data.keys()
                    if not f:
                        print(data)
                        print(field)
                        break

                print(f"f = {f}")
                if f:
                    g = 1
                    for travel in created_trips:
                        g *= not data['title'] == travel['title']
                    if g:
                        add_travell(data)
        else:
            return HttpResponse("Error")
    return render(req, 'exporter.html')

def download_and_save_json(request):
    http_response = HttpResponse(json.dumps(created_trips), content_type='application/json')
    http_response['Content-Disposition'] = f'attachment; filename="all_travels.json"'
    return http_response


def download_and_save_xml(request):
    http_response = HttpResponse(dict_to_xml_string(created_trips), content_type='application/xml')
    http_response['Content-Disposition'] = f'attachment; filename="all_travels.xml"'
    return http_response


@require_POST
def ajax_search_trips(request):
    search_query = request.POST.get('search', '').strip()
    result_type = request.POST.get('result_type', 'db')  # по умолчанию из БД

    trips = []

    if result_type == 'db':
        trips_qs = Trip.objects.all()
        if search_query:
            trips_qs = trips_qs.filter(
                title__icontains=search_query
            ) | trips_qs.filter(
                country__icontains=search_query
            ) | trips_qs.filter(
                discription__icontains=search_query
            )
        for trip in trips_qs:
            trips.append({
                'id': trip.id,
                'title': trip.title,
                'discription': trip.discription,
                'country': trip.country,
                'date_in': trip.date_in,
                'date_out': trip.date_out,
                'price': trip.price
            })

    elif result_type == 'json':
        for trip in created_trips.values():
            if search_query:
                if (
                    search_query.lower() in trip.get('title', '').lower() or
                    search_query.lower() in trip.get('country', '').lower() or
                    search_query.lower() in trip.get('discription', '').lower()
                ):
                    trips.append(trip)
            else:
                trips.append(trip)
    else:
        trips_qs = Trip.objects.all()
        if search_query:
            trips_qs = trips_qs.filter(
                title__icontains=search_query
            ) | trips_qs.filter(
                country__icontains=search_query
            ) | trips_qs.filter(
                discription__icontains=search_query
            )
        for trip in trips_qs:
            trips.append({
                'id': trip.id,
                'title': trip.title,
                'discription': trip.discription,
                'country': trip.country,
                'date_in': trip.date_in,
                'date_out': trip.date_out,
                'price': trip.price
            })
        for trip in created_trips.values():
            if search_query:
                if (
                    search_query.lower() in trip.get('title', '').lower() or
                    search_query.lower() in trip.get('country', '').lower() or
                    search_query.lower() in trip.get('discription', '').lower()
                ):
                    trips.append(trip)
            else:
                trips.append(trip)

    # Рендерим только карточки поездок (частичный шаблон)
    html = render_to_string('trip_cards.html', {'trips': trips}, request=request)

    return HttpResponse(html)


@require_POST
def delete_travel(request):
    print(created_trips)
    travel_id = request.POST.get('travel_id')

    if Trip.objects.filter(id=travel_id).exists():
        Trip.objects.get(id=travel_id).delete()
        print(Trip.objects.all().values())
        return JsonResponse({
            'status': 'deleted'
        })
    elif os.path.exists(os.path.join('travells', str(travel_id))):
        file_path = os.path.join('travells', str(travel_id))
        os.remove(file_path)
        del created_trips[travel_id]
        return JsonResponse({
            'status': 'deleted'
        })
    else:
        return JsonResponse({
            'status': 'not exists'
        })


def change_travel(req, travel_id):
    if req.method == 'POST':
        print(req.POST)
        trip = Trip.objects.get(id=req.POST.get('trip_id'))
        if trip.title != req.POST.get('title'):
            trip.title = req.POST.get('title')
        if trip.discription != req.POST.get('discription').strip() and req.POST.get('discription').strip() != "":
            trip.discription = req.POST.get('discription').strip()
        if trip.country != req.POST.get('country'):
            trip.country = req.POST.get('country')
        if '-' in req.POST.get('date_in'):
            new_date_in = req.POST.get('date_in').split('-')
            new_date_in = f'{new_date_in[2]}.{new_date_in[1]}.{new_date_in[0]}'
        if trip.date_in != new_date_in:
            trip.date_in = new_date_in
        if '-' in req.POST.get('date_out'):
            new_date_out = req.POST.get('date_out').split('-')
            new_date_out = f'{new_date_out[2]}.{new_date_out[1]}.{new_date_out[0]}'
        if trip.date_out != new_date_out:
            trip.date_out = new_date_out
        if trip.price != req.POST.get('price'):
            trip.price = req.POST.get('price')
        trip.save()
    if Trip.objects.filter(id=travel_id).exists():
        trip = Trip.objects.get(id=travel_id)
        return render(req, 'edit_travel.html', {'trip': trip})
    elif os.path.exists(f'travells\\{travel_id}'):
        trip = created_trips[travel_id]
        return render(req, 'edit_travel.html', {'trip': trip})
    else:
        return HttpResponse('Не найдено')

