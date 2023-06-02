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
            annotate(datetime=F('datetime__datetime'))

        return {'points': queryset}

    @debug_time_func
    def get_points_fires_today(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(datetime__datetime__date=FuncTemplateOverride(template="current_date"))
        )

        return queryset

    def get_points_after_twentyfour(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(datetime__datetime__lte=FuncTemplateOverride(template="NOW()"))
                       & Q(datetime__datetime__gte=FuncTemplateOverride(template="NOW() - interval '24 hours'"))
        )

        return queryset

    def get_points_after_week(self, request, *args, **kwargs):
        queryset = self.__get_queryset(
            filter_set=Q(datetime__datetime__lte=FuncTemplateOverride(template="NOW()"))
                       & Q(datetime__datetime__gte=FuncTemplateOverride(template="NOW() - interval '1 week'"))
        )

        return queryset

    # def fetch_filter_set(self, request, parameter):
    #     date_min = request.GET.get(DATE_MIN, None)
    #     date_max = request.GET.get(DATE_MAX, None)
    #     date = request.GET.get(DATE, None)
    #
    #     if date_min and date_max and date_max != date_min:
    #         filter_set = Q(datetime__datetime__gte=date_min) \
    #                      & Q(datetime__datetime__lte=date_max)
    #     elif date:
    #         filter_set = Q(datetime__datetime__date=date)
    #     else:
    #         return []
    #
    #     return filter_set

    @debug_time_func
    def get_points_fires(self, request, *args, **kwargs):

        date_min = request.GET.get(DATE_MIN, None)
        date_max = request.GET.get(DATE_MAX, None)
        date = request.GET.get(DATE, None)

        if date_min and date_max and date_max != date_min:
            filter_set = Q(datetime__datetime__gte=date_min) \
                         & Q(datetime__datetime__lte=date_max)
        elif date:
            filter_set = Q(datetime__datetime__date=date)
        else:
            return []
        # if self.fetch_filter_set(request, datetime__datetime) == []
        queryset = self.__get_queryset(filter_set=filter_set)

        return queryset

    @staticmethod
    def get_fire_values_for_pdf_shp(subject_tag, date_time):
        return FireValue.objects.select_related('district', 'settlement', 'datetime').\
            filter(district__subject__tag=subject_tag, tech=False, datetime__datetime=date_time)


class SettlementLeast5:

    def get_settlement_least_5km(self, request, *args, **kwargs):

        date_min = request.GET.get(DATE_MIN, None)
        date_max = request.GET.get(DATE_MAX, None)
        date = request.GET.get(DATE, None)
        list_ids = request.GET.get(LIST_IDS, None)

        if date_min and date_max and date_max != date_min:
            filter_set = Q(fire_value__datetime__datetime__gte=date_min) \
                         & Q(fire_value__datetime__datetime__lte=date_max)
        elif date:
            filter_set = Q(fire_value__datetime__datetime__date=date)
        else:
            return [] #filter_set&

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

    def get_dates(self, request, *args, **kwargs):

        queryset = self.model.\
            objects.\
            annotate(formatted_date=Func(F('datetime'),
                                         Value('YYYY-MM-DD'),
                                         function='to_char',
                                         output_field=CharField())).\
            distinct('formatted_date').values('formatted_date')

        date_json = self.do_format_date(queryset)

        return {
            'date': date_json
        }

    @staticmethod
    def format_time_of_date(queryset):
        output_dict = {}
        for item in queryset:
            date = item['datetime'].strftime('%Y-%m-%d')
            time = item['datetime'].strftime('%H:%M')
            if not output_dict.get(date):
                output_dict[date] = []
            output_dict[date].append(time)
        return output_dict

    def get_time_of_date(self, request, *args, **kwargs):
        date_min = request.GET.get(DATE_MIN, None)
        date_max = request.GET.get(DATE_MAX, None)
        date = request.GET.get(DATE, None)

        if date_min and date_max and date_max != date_min:
            filter_set = Q(datetime__gte=date_min) \
                         & Q(datetime__lte=date_max)
        elif date:
            filter_set = Q(datetime__date=date)
        else:
            return []

        queryset = self.model.\
            objects.\
            filter(filter_set).\
            values('datetime')

        return {
            'time': self.format_time_of_date(queryset)
        }



