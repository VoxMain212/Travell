# planner/tests.py
import os
import json
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Trip


class PlannerTestCase(TestCase):

    def setUp(self):
        Trip.objects.all().delete()
        self.travells_dir = 'travells'
        os.makedirs(self.travells_dir, exist_ok=True)
        # Очищаем папку
        for f in os.listdir(self.travells_dir):
            os.remove(os.path.join(self.travells_dir, f))

    def tearDown(self):
        # Удаляем папку после тестов
        for f in os.listdir(self.travells_dir):
            os.remove(os.path.join(self.travells_dir, f))
        os.rmdir(self.travells_dir)

    def test_trip_model(self):
        trip = Trip.objects.create(
            id="test123",
            title="Япония",
            discription="Поездка в Токио",
            country="japan",
            date_in="01.06.2025",
            date_out="10.06.2025",
            price=150000
        )
        self.assertEqual(trip.title, "Япония")

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_planner_page_loads(self):
        response = self.client.get(reverse('planner'))
        self.assertEqual(response.status_code, 200)

    def test_create_trip_in_db(self):
        form_data = {
            'title': 'Новая поездка',
            'discription': 'Описание',
            'country': 'greece',
            'date_in': '2025-08-01',      # ← только дата
            'date_out': '2025-08-10',
            'export': 'db',
            'price': 120000
        }
        response = self.client.post(reverse('planner'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Trip.objects.filter(title='Новая поездка').exists())

    def test_export_trip_to_json(self):
        form_data = {
            'title': 'Экспорт в JSON',
            'discription': 'Тест',
            'country': 'iceland',
            'date_in': '2025-09-01',
            'date_out': '2025-09-10',
            'export': 'json',
            'price': 300000
        }
        response = self.client.post(reverse('planner'), form_data)
        # Проверяем, что это JSON-ответ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment; filename="new_travel.json"', response['Content-Disposition'])

    def test_upload_json_file(self):
        json_content = json.dumps({
            'title': 'Загруженная поездка',
            'discription': 'Из файла',
            'country': 'brazil',
            'date_in': '01.01.2026',
            'date_out': '10.01.2026',
            'price': 250000
        })
        file = SimpleUploadedFile("trip.json", json_content.encode(), content_type="application/json")
        response = self.client.post(reverse('export'), {'file': file})
        self.assertEqual(response.status_code, 200)
        files = os.listdir(self.travells_dir)
        self.assertEqual(len(files), 1)

    def test_delete_json_trip(self):
        trip_id = 'json_del_test'
        file_path = os.path.join(self.travells_dir, trip_id)
        with open(file_path, 'w') as f:
            json.dump({'id': trip_id, 'title': 'Удалить'}, f)

        self.assertTrue(os.path.exists(file_path))
        response = self.client.post(reverse('delete_travel'), {'travel_id': trip_id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists(file_path))

    def test_download_all_json(self):
        response = self.client.get(reverse('download_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_download_all_xml(self):
        response = self.client.get(reverse('download_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')