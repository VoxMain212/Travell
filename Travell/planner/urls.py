from django.urls import path
from .views import index, planner, exporter, download_and_save_json, download_and_save_xml


urlpatterns = [
    path('', index, name='home'),
    path('planner', planner, name='planner'),
    path('exporter', exporter, name='export'),
    path('download_json', download_and_save_json, name='download_json'),
    path('download_xml', download_and_save_xml, name='download_xml')
]