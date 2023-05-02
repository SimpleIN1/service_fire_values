import json

from django.db.models import Q, Func, F, Value, CharField, Count

from FireApp.decorators import debug_time_func
from FireApp.models import FireValue, DateTime, SettlementFireValue

DATE_MIN = 'date_min'
DATE_MAX = 'date_max'
DATE = 'date'
LIST_IDS = 'list_ids'


class FuncTemplateOverride(Func):

    def __init__(self, template,
                 *expressions,
                 **extra):
        super().__init__(*expressions,
                         **extra)
        self.template = template


class PointsForGetDataAboutFires:
    database = 'remoteFiresDb'
    model = FireValue

    def __get_queryset(self, filter_set):

        queryset = self.model. \
            objects. \
            select_related('date'). \
            filter(filter_set&Q(tech=False)). \
            values('temperature', 'longitude', 'latitude'). \
            annotate(datetime=F('date__date'))

        return {'points': queryset}

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
            filter_set = Q(date__date__date=date)
        else:
            return []

        queryset = self.__get_queryset(filter_set=filter_set)

        return queryset

    @staticmethod
    def get_fire_values_for_pdf(subject_tag, date_time):
        return FireValue.objects.select_related('district', 'settlement', 'date', 'satellite').\
            filter(district__subject__tag=subject_tag, tech=False, date__date=date_time)


class SettlementLeast5:

    def get_settlement_least_5km(self, request, *args, **kwargs):

        date_min = request.GET.get(DATE_MIN, None)
        date_max = request.GET.get(DATE_MAX, None)
        date = request.GET.get(DATE, None)
        list_ids = request.GET.get(LIST_IDS, None)

        if date_min and date_max and date_max != date_min:
            filter_set = Q(fire_value__date__date__gte=date_min) \
                         & Q(fire_value__date__date__lte=date_max)
        elif date:
            filter_set = Q(fire_value__date__date__date=date)
        else:
            return [] #filter_set&

        print(12)

        queryset = SettlementFireValue. \
            objects. \
            select_related('fire_value'). \
            filter(filter_set&Q(fire_value__tech=False)). \
            values('settlement_id'). \
            annotate(Count('settlement_id')) .\
            values('settlement_id')

        if list_ids in ('y', 'yes', 't', 'true', 'on', '1'):
            ql = map(lambda x: x['settlement_id'], queryset)
        elif list_ids in ('n', 'no', 'f', 'false', 'off', '0'):
            ql = queryset
        else:
            ql = queryset

        return {'settlement_ids': ql}


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
            date = item['formatted_date']
            year, months, day = date.split('-')

            if not out_json.get(year):
                out_json[year] = {}
            if not out_json[year].get(months):
                out_json[year][months] = []

            if not (date in out_json[year][months]):
                out_json[year][months].append(date)

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



