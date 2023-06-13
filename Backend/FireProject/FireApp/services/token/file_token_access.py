
from datetime import datetime

from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36

from django.contrib.auth.tokens import PasswordResetTokenGenerator #as TokenGenerator
from django.conf import settings


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user_uuid, timestamp): #Override. Changed user.password to user.uuid
        return f"{user_uuid}{settings.SECRET_KEY}{timestamp}_file_access"

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        #print('--',user, token)
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False


        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
 
           #print('==', token, self._make_token_with_timestamp(user, ts, secret))
           if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.PASSWORD_RESET_TIMEOUT:
            return False

        return True


def create_token(
        user_uuid,
):
    '''# Гененрация токена для отправки по почте #'''

    return TokenGenerator().make_token(user_uuid)


def check_token(
        user_uuid,
        getting_token: str,
) -> bool:
    '''# Проверка токена #'''

    return TokenGenerator().check_token(user_uuid, getting_token)
