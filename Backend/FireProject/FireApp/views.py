
from .services.viewsets import FiresViewset
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