
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class FiresViewset(APIView):
    queryset_func_link = None
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.queryset_func_link(request, args, kwargs)
        return Response(queryset, status=status.HTTP_200_OK)
