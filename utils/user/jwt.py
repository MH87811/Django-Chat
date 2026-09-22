from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from accounts.models import RefreshTokenSession

User = get_user_model()

class TokenUtils:
    ACCESS_TOKEN_TYPE = 'access'
    REFRESH_TOKEN_TYPE = 'refresh'

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @classmethod
    def save_hash_token(cls, token):
        hash_token = make_password(token)
        token_detail = RefreshToken(token)
        RefreshTokenSession.objects.create(
            user_id=token_detail['user_id'],
            jti=token_detail['jti'],
            expires_at=timezone.datetime.fromtimestamp(
                token_detail['exp'],
                tz=timezone.get_current_timezone(),
            ),
            hashed_token=hash_token,
        )

    @classmethod
    def validate_token(cls, token, token_type):
        if token_type not in [cls.ACCESS_TOKEN_TYPE, cls.REFRESH_TOKEN_TYPE]:
            raise TokenError('Invalid Token Type.')
        match token_type:
            case cls.ACCESS_TOKEN_TYPE:
                token = AccessToken(token)

            case cls.REFRESH_TOKEN_TYPE:
                token = RefreshToken(token)
                try:
                    token_record = RefreshTokenSession.objects.get(jti=token['jti'])
                except RefreshTokenSession.DoesNotExist:
                    raise TokenError('Token Not Found')
                if not check_password(str(token), token_record.hashed_token):
                    raise TokenError('Invalid Token')
                if token_record.is_revoked:
                    cls.revoke_tokens(token['user_id'])
                    raise TokenError('Token Has Already Been Revoked.')
        return token

    @classmethod
    def revoke_token(cls, token):
        token = cls.validate_token(token, cls.REFRESH_TOKEN_TYPE)
        token_record = RefreshTokenSession.objects.get(jti=token['jti'])
        token_record.is_revoked = True
        token_record.revoked_at = timezone.now()
        token_record.save(update_fields=['is_revoked', 'revoked_at'])

    @classmethod
    def revoke_tokens(cls, user_id):
        RefreshTokenSession.objects.filter(user_id=user_id, is_revoked=False).update(is_revoked=True, revoked_at=timezone.now())

    @classmethod
    @transaction.atomic
    def rotate(cls, refresh_token):
        cls.validate_token(refresh_token, cls.REFRESH_TOKEN_TYPE)

        old_refresh = RefreshToken(refresh_token)

        user_id = old_refresh["user_id"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise TokenError('User Not Found')

        new_tokens = cls.generate_tokens(user)
        cls.save_hash_token(new_tokens['refresh'])
        cls.revoke_token(refresh_token)

        return {
            "access": str(new_tokens['access']),
            "refresh": str(new_tokens['refresh']),
        }