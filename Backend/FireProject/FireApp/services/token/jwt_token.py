from django.conf import settings
import jwt

from FireApp.decorators import exception_jwt


class Jwt:

    @staticmethod
    @exception_jwt
    def get_payload_from_access_token(token):

        payload = jwt.decode(
            jwt=token,
            key=settings.ACCESS_SECRET_KEY,
            algorithms='HS256'
        )

        return payload

