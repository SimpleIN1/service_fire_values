from rest_framework.authentication import BaseAuthentication

from FireApp.services.token.jwt_token import Jwt


class RemoteUserAuthentication(BaseAuthentication):

    def authenticate(self, request):

        token = request.headers.get('Authorization', None)

        #print(token)

        if token is None:
            return None

        try:
            token = token.split(' ')[1]
        except IndexError:
            return None
        #print(token)
        payload = Jwt.get_payload_from_access_token(token)

        # if payload is None:
        #     raise exceptions.AuthenticationFailed(
        #         detail='Token is invalid or expired',
        #         code=status.HTTP_401_UNAUTHORIZED
        #     )
        user = self.User(True, payload['jti'])
        # print('REMOTE')
        return (user, None)

    class User:
        def __init__(self, is_authenticated, jti):
            self.is_authenticated = is_authenticated
            self.jti = jti
