from django.urls import path
from .views import index, planner


urlpatterns = [
    path('', index, name='home'),
    path('/planner', planner, name='planner')
]