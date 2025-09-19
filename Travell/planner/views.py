from django.shortcuts import render, HttpResponse
from .forms import TripForm, FileForm
from uuid import uuid4
import os
import json
from xml.dom.minidom import parseString
import dicttoxml
import xml.etree.ElementTree as ET

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


def add_travell(travel_info: dict):
    print(travel_info)
    with open(f'travells\\{uuid4().hex}', 'w', encoding='utf-8') as f:
        json.dump(travel_info, f)
    created_trips.append(travel_info)


def load_travells():
    if not os.path.exists('travells'):
        return
    for file in os.listdir('travells'):
        with open(f'travells\\{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
        created_trips.append(data)


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
            if form.cleaned_data['export'] == 'json':
                http_response = HttpResponse(json.dumps(cleaned_data), content_type='application/json')
                http_response['Content-Disposition'] = f'attachment; filename="new_travel.json"'
                return http_response
            elif form.cleaned_data['export'] == 'xml':
                http_response = HttpResponse(dict_to_xml_string(cleaned_data), content_type='application/xml')
                http_response['Content-Disposition'] = f'attachment; filename="new_travel.xml"'
                return http_response
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
