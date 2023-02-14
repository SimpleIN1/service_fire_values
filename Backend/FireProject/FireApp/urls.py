
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (FiresAPIView,
                    DaysFiresAPIView,
                    FiresTodayAPIView,
                    FiresAfterTwentyFourAPIView,
                    FiresAfterWeekAPIView)


urlpatterns = [
    path('points/', FiresAPIView.as_view(), name='fires'),
    path('points/today/', FiresTodayAPIView.as_view(), name='fires after today'),
    path('points/twentyfourhours/', FiresAfterTwentyFourAPIView.as_view(), name='fires after 24 hours'),
    path('points/week/',FiresAfterWeekAPIView.as_view(), name='fires after week'),
    path('days/', DaysFiresAPIView.as_view(), name='day fires'),
]