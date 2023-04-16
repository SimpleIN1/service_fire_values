import time

from django.db.models import Q, Func, F, Value, CharField

from .decorators import query_debugger, debug_time_func
from FireApp.models import FireValues, DateTime


DATE_MIN = 'date_min'
DATE_MAX = 'date_max'
DATE = 'date'


class FuncTemplateOverride(Func):

    def __init__(self, template,
                 *expressions,
                 **extra):
        super().__init__(*expressions,
                         **extra)
        self.template = template


class PointsForGetDataAboutFires:
    database = 'remoteFiresDb'
    model = FireValues

    def __get_queryset(self, filter_set):

        queryset = self.model. \
            objects. \
            select_related('date'). \
            filter(filter_set). \
            values('temperature', 'longitude', 'latitude'). \
            annotate(datetime=F('date__date'))

        return {'points': queryset}
        # return JsonResponse(queryset)

    @debug_time_func
    def get_points_fires_today(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(date__date__date=FuncTemplateOverride(template="current_date"))
        )

        return queryset

    def get_points_after_twentyfour(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(date__date__lte=FuncTemplateOverride(template="NOW()"))
                       & Q(date__date__gte=FuncTemplateOverride(template="NOW() - interval '24 hours'"))
        )

        return queryset

    def get_points_after_week(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(date__date__lte=FuncTemplateOverride(template="NOW()"))
                       & Q(date__date__gte=FuncTemplateOverride(template="NOW() - interval '1 week'"))
        )

        return queryset

    @debug_time_func
    def get_points_fires(self, request, *args, **kwargs):

        date_min = request.GET.get(DATE_MIN, None)
        date_max = request.GET.get(DATE_MAX, None)
        date = request.GET.get(DATE, None)

        if date_min and date_max and date_max != date_min:
            filter_set = Q(date__date__gte=date_min) \
                         & Q(date__date__lte=date_max)
        elif date:
            # print(date)
            filter_set = Q(date__date__date=date)#Q(date_id__lte=DateTime.objects.filter(date__date=date).annotate(max=Max('id'))) \
                         #& Q(date_id__gte=DateTime.objects.filter(date__date=date).annotate(max=Min('id')))
        else:
            return []

        queryset = self.__get_queryset(filter_set=filter_set)
        return queryset




'''
json
{
    date:[
        year:[
            month: [
                    
            ],
            month: [
                    
            ]    
        ],
        year:[
            
        ],
    ]
}

'''


class DateUnique:
    database = 'remoteFiresDb'
    model = DateTime

    @staticmethod
    def do_format_date(queryset):
        '''
        :param queryset: набор даты из базы данных
        :return: отформатированные даты для клиента
        '''
        out_json = {}

        for item in queryset:
            year, months, day = item['formatted_date'].split('-')

            if not out_json.get(year):
                out_json[year] = {}
            if not out_json[year].get(months):
                out_json[year][months] = []

            if not (day in out_json[year][months]):
                out_json[year][months].append(day)

        return out_json

    @debug_time_func
    def get_dates(self, request, *args, **kwargs):

        queryset = self.model.\
            objects.\
            annotate(formatted_date=Func(F('date'),
                                         Value('YYYY-MM-DD'),
                                         function='to_char',
                                         output_field=CharField())).\
            distinct('formatted_date').values('formatted_date')

        date_json = self.do_format_date(queryset)

        return {
            'date': date_json
        }



