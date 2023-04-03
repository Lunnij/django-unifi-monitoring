from django import forms
from django.views.generic.edit import FormMixin

from unifi.shared import get_all_sites

SITES_CHOICES = [(site['name'], site['desc']) for site in get_all_sites()]
PERIOD_CHOICES = [
    ('-1', 'interval does not specified'),
    ('900', '15 minutes'),
    ('1200', '20 minutes'),
]


class LoggerForm(FormMixin, forms.Form):
    site_selector = forms.ChoiceField(choices=SITES_CHOICES, widget=forms.Select(attrs={'class': 'container'}))
    period_selector = forms.ChoiceField(choices=PERIOD_CHOICES, widget=forms.Select(attrs={'class': 'container'}))
