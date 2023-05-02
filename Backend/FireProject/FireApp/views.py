import json
import time

from django.db.models import F
from django.http import HttpResponse, JsonResponse, FileResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from FireApp.services.settlement import get_settlement
from FireApp.viewsets import FiresViewset, BaseAPIView
from FireApp.serializers import PDFSerializer, ShapeSerializer
from FireApp.services.pdf.pdf import PDF
from FireApp.services.process_fires import (PointsForGetDataAboutFires as Points,
                                            DateUnique as Date, SettlementLeast5, PointsForGetDataAboutFires)
from FireApp.services.shapefile import ShpFile


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


class SettlementLeast5APIView(FiresViewset, Date):
    queryset_func_link = SettlementLeast5.get_settlement_least_5km


class TestAPIView(APIView):
    def get(self, request, *args, **kwargs):
        temp_list = [{
            'item_id': item_id,
            'item_rev': 10000 - item_id,
            'item_other': 1000 - item_id,
            'name': '12dasdasdasdasdasdasdasdasdasd',
        } for item_id in range(3000, 10000)]
        # print(temp_list)
        return JsonResponse({'temp_list': temp_list})
        # return HttpResponse(json.dumps({'temp_list': temp_list}))
        # queryset = FireValues. \
        #     objects. \
        #     select_related('date'). \
        #     filter(date__date__date='2022-05-11'). \
        #     values('temperature', 'longitude', 'latitude'). \
        #     annotate(datetime=F('date__date'))
        # return Response({queryset})


class ShapeFileLoadAPIView(BaseAPIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = ShapeSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        # print('Start function')
        # start = time.perf_counter()

        queryset = PointsForGetDataAboutFires.get_fire_values_for_pdf(
            serializer.data['subject_tag'],
            serializer.data['date_time'],
            # subject_tag='ALTAY',
            # date_time='2022-05-16T05:05:00',
        )
        shp = ShpFile(
            queryset=queryset,
            **serializer.data
            # subject_tag='ALTAY',
            # date_time='2022-05-16T05:05:00',
        )

        if queryset.exists():
            if shp.is_exist_file(shp.get_path_to_file()):
                filename = shp.get_path_to_file()
            else:
                filename = shp.make_archive()
        else:
            return Response({'file_info': 'Data is not(1)'})
        # end = time.perf_counter()
        # print(f'Time of work - {(end - start):.4f}s')
        return FileResponse(open(filename, 'rb'))


class PDFLoadAPIView(BaseAPIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = PDFSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        # print('Start function')
        # start = time.perf_counter()
        queryset = PointsForGetDataAboutFires.get_fire_values_for_pdf(
            serializer.data['subject_tag'],
            serializer.data['date_time']
        )

        pdf = PDF(
            queryset=queryset,
            **serializer.data
            # date_time='2020-12-12T12:22:22',  # datetime.datetime.now(),
            # cloud_shielding=80,
            # operator_fio='Илюхин Р.А.',
            # subject_tag='ALTAY'
        )
        if queryset.exists():
            if pdf.is_exist_file(pdf.get_path_to_file()):
                filename = pdf.get_path_to_file()
            else:
                filename = pdf.build_file()
        else:
            return Response({'file_inf': 'Data is not(1)'})
        # end = time.perf_counter()
        # print(f'Time of work - {(end - start):.4f}s')
        return FileResponse(open(filename, 'rb'))


# class SettlementAPIView(APIView):
#     # permission_classes = (IsAuthenticated,)
#     def get(self, request, *args, **kwargs):
#         queryset = get_settlement()
#         return Response({'settlements': queryset})



