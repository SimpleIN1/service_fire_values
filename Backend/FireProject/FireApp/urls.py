
from django.urls import path
from django.views.decorators.cache import cache_page

from FireApp.views import (FiresAPIView,
                           DaysFiresAPIView,
                           FiresTodayAPIView,
                           FiresAfterTwentyFourAPIView,
                           FiresAfterWeekAPIView,
                           TestAPIView, PDFLoadAPIView,
                           ShapeFileLoadAPIView,
                           SettlementLeast5APIView)


urlpatterns = [
    path('points/', FiresAPIView.as_view(), name='fires'),
    path('points/today/', FiresTodayAPIView.as_view(), name='fires after today'),
    path('points/twentyfourhours/', FiresAfterTwentyFourAPIView.as_view(), name='fires after 24 hours'),
    path('points/week/', FiresAfterWeekAPIView.as_view(), name='fires after week'),
    path('days/', DaysFiresAPIView.as_view(), name='day fires'),

    path('load/pdf/', PDFLoadAPIView.as_view(), name='pdf'),
    path('load/shapefile/', ShapeFileLoadAPIView.as_view(), name='shapefile'),
    path('settlement_least_5/', SettlementLeast5APIView.as_view(), name='shapefile'),
    # path('settlement/', SettlementAPIView.as_view(), name='shapefile'),
]