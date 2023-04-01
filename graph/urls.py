from django.urls import path
from django.views.generic import TemplateView

from .forms import chart


urlpatterns = [
    path('', TemplateView.as_view(template_name='graph.html'), name='index'),
    path('bar-json/', chart, name='bar_json'),
]