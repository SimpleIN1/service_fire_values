
from rest_framework import status, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class FiresViewset(APIView):
    queryset_func_link = None
   # permission_classes = (IsAuthenticated, )

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

    def get(self, request, *args, **kwargs):
        queryset = self.queryset_func_link(request, args, kwargs)
        return Response(queryset, status=status.HTTP_200_OK)
        # return HttpResponse(json.dumps(queryset))
        # return Response({'queryset':'12'})