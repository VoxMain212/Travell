from django.urls import path
from .views import index, planner, exporter, download_and_save_json, download_and_save_xml, ajax_search_trips, delete_travel, change_travel


urlpatterns = [
    path('', index, name='home'),
    path('planner', planner, name='planner'),
    path('exporter', exporter, name='export'),
    path('download_json', download_and_save_json, name='download_json'),
    path('download_xml', download_and_save_xml, name='download_xml'),
    path('ajax/search-trips/', ajax_search_trips, name='ajax_search_trips'),
    path('delete_travel', delete_travel, name='delete_travel'),
    path('change_travel/<slug:travel_id>/', change_travel, name='change_travel')
]