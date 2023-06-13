from datetime import datetime
import pytz
from django.db.models.functions import TruncMinute
from django.db.models import Count
from django.http import JsonResponse
from django.views import View

from logger.models import Device


class BarChartJSONView(View):
    def get(self, request, *args, **kwargs):
        #
        start_date_str = request.GET.get('start')
        end_date_str = request.GET.get('end')

        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        #
        queryset = Device.objects \
            .filter(logged_at__range=[start_date, end_date]) \
            .annotate(altered_logged_at=TruncMinute('logged_at')) \
            .values('altered_logged_at', 'site_id') \
            .annotate(mac_count=Count('mac', distinct=True)) \
            .distinct() \
            .order_by('altered_logged_at')

        #
        dataset_label = []
        for obj in queryset:
            if obj['site_id'] not in dataset_label:
                dataset_label.append(obj['site_id'])

        #
        labels = []
        for obj in queryset:
            if obj['altered_logged_at'].strftime('%d.%m %H:%M') not in labels:
                labels.append(obj['altered_logged_at'].strftime('%d.%m %H:%M'))

        #
        datasets_dict = {label: [0] * len(labels) for label in dataset_label}
        for obj in queryset:
            label = obj['site_id']
            data_index = labels.index(obj['altered_logged_at'].strftime('%d.%m %H:%M'))
            datasets_dict[label][data_index] = obj['mac_count']

        #
        datasets = []
        total_data = [0] * len(labels)

        for label in dataset_label:
            data = datasets_dict[label]
            dataset = {
                'label': label,
                'data': data,
                'borderWidth': 1,
                'tension': 0.5,
                'pointRadius': 0
            }
            datasets.append(dataset)
            total_data = [total_data[i] + data[i] for i in range(len(labels))]

        total_dataset = {
            'label': 'All data',
            'data': total_data,
            'borderWidth': 1,
            'tension': 0.5,
            'pointRadius': 0
        }
        datasets.append(total_dataset)

        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        return JsonResponse(chart_data)


chart = BarChartJSONView.as_view()
