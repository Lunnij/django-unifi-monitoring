from datetime import datetime 
import pytz
from django.db.models.functions import TruncMinute
from django.db.models import Count
from django.http import JsonResponse
from django.views import View

from logger.models import Network


class BarChartJSONView(View):
    def get(self, request, *args, **kwargs):
        #
        start_date_str = request.GET.get('start')
        end_date_str = request.GET.get('end')
        
        default_timezone = pytz.timezone('UTC')
        start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=default_timezone)
        end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=default_timezone)
        
        #
        queryset = Network.objects \
            .filter(logged_at__range=[start_date, end_date]) \
            .annotate(altered_logged_at=TruncMinute('logged_at')) \
            .values('altered_logged_at', 'network_name') \
            .exclude(network_name='offline')\
            .annotate(mac_count=Count('mac', distinct=True)) \
            .distinct() \
            .order_by('altered_logged_at')
        
        #
        dataset_label = []
        for obj in queryset:
            if obj['network_name'] not in dataset_label:
                dataset_label.append(obj['network_name'])
        
        #
        labels = []
        for obj in queryset:
            if obj['altered_logged_at'].strftime('%d.%m %H:%M') not in labels:
                labels.append(obj['altered_logged_at'].strftime('%d.%m %H:%M'))
        
        #
        datasets_dict = {label: [0] * len(labels) for label in dataset_label}
        for obj in queryset:
            label = obj['network_name']
            data_index = labels.index(obj['altered_logged_at'].strftime('%d.%m %H:%M'))
            datasets_dict[label][data_index] = obj['mac_count']
        
        #
        datasets = []
        for label in dataset_label:
            dataset = {
                'label': label,
                'data': datasets_dict[label],
                'borderWidth': 1
            }
            datasets.append(dataset)
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        return JsonResponse(chart_data)


chart = BarChartJSONView.as_view()

