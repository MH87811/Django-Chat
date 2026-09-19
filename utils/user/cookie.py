from django.conf import settings


class CookieUtil:
    REFRESH_TOKEN_COOKIE_NAME = 'refresh_token'

    @classmethod
    def set_refresh_token(cls, response, token):
        response.set_cookie(
            key=cls.REFRESH_TOKEN_COOKIE_NAME,
            value=token,
            max_age= 30 * 24 * 60 * 60,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
    @classmethod
    def get_refresh_token(cls, request):
        return request.COOKIES.get(cls.REFRESH_TOKEN_COOKIE_NAME)

    @classmethod
    def delete_refresh_token(cls, response):
        response.delete_cookie(
            key=cls.REFRESH_TOKEN_COOKIE_NAME,
            samesite="Lax",
        )