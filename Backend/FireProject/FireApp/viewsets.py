import json
import time

from django.core import serializers
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from rest_framework import status, exceptions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class BaseAPIView(APIView):

    def permission_denied(self, request, message=None, code=None): # override
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if request.authenticators and not request.successful_authenticator:
            # raise OverrideNotAuthenticated()
            raise exceptions.AuthenticationFailed(
                {'auth_error': '20'}
            )
        raise exceptions.PermissionDenied(detail=message, code=code)


class FiresViewset(BaseAPIView):
    queryset_func_link = None
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):

        date = request.GET.get('date')
        if date:
            try:
                time.strptime(date, '%Y-%m-%d')
            except ValueError:
                return Response({'fields_error': '18'}, status=400)

        queryset = self.queryset_func_link(request, args, kwargs)
        return Response(queryset, status=status.HTTP_200_OK)

