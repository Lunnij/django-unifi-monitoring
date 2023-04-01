from django import forms
from django.views.generic.edit import FormMixin

from unifi.shared import get_all_sites

SITES_CHOICES = [(site['name'], site['desc']) for site in get_all_sites()]
PERIOD_CHOICES = [
    ('-1', 'interval does not specified'),
    ('30', '30 seconds'),
    ('120', '2 minutes'),
]


class LoggerForm(FormMixin, forms.Form):
    site_selector = forms.ChoiceField(choices=SITES_CHOICES, widget=forms.Select(attrs={'class': 'container'}))
    period_selector = forms.ChoiceField(choices=PERIOD_CHOICES, widget=forms.Select(attrs={'class': 'container'}))
