import json

from django.db.models import F
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from FireApp.viewsets import FiresViewset
from .models import FireValues
from .services.process_fires import (PointsForGetDataAboutFires as Points,
                                     DateUnique as Date)


class FiresTodayAPIView(FiresViewset, Points):
    queryset_func_link = Points.get_points_fires_today


class FiresAfterTwentyFourAPIView(FiresViewset, Points):
    queryset_func_link = Points.get_points_after_twentyfour


class FiresAfterWeekAPIView(FiresViewset, Points):
    queryset_func_link = Points.get_points_after_week


class FiresAPIView(FiresViewset, Points):
    queryset_func_link = Points.get_points_fires


class DaysFiresAPIView(FiresViewset, Date):
    queryset_func_link = Date.get_dates


class TestAPIView(APIView):
    def get(self, request, *args, **kwargs):
        temp_list = [{
            'item_id': item_id,
            'item_rev': 10000 - item_id,
            'item_other': 1000 - item_id,
            'name': '12dasdasdasdasdasdasdasdasdasd',
        } for item_id in range(3000, 10000)]
        # print(temp_list)
        return Response({'temp_list': temp_list})
        # return HttpResponse(json.dumps({'temp_list': temp_list}))
        # queryset = FireValues. \
        #     objects. \
        #     select_related('date'). \
        #     filter(date__date__date='2022-05-11'). \
        #     values('temperature', 'longitude', 'latitude'). \
        #     annotate(datetime=F('date__date'))
        # return Response({queryset})