from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.exceptions import TokenError
from utils.core.response_buider import ResponseBuilder
from utils.user.jwt import TokenUtils
from utils.user.cookie import CookieUtil

# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny,]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                tokens = TokenUtils.generate_tokens(user)
                TokenUtils.save_hash_token(tokens['refresh'])
                response = ResponseBuilder.success(
                    message='Registration successful.',
                    detail={
                        'user': serializer.data,
                        "access": tokens['access']
                    },
                    status_code=status.HTTP_201_CREATED,
                )
                CookieUtil.set_refresh_token(response, tokens['refresh'])
                return response
            except (DjangoValidationError, DRFValidationError) as e:
                return ResponseBuilder.error(
                    message='Registration failed due validation failure.',
                    error_code='VALIDATION_FAILED',
                    error=str(e),
                )

        return ResponseBuilder.error(
            message='Registration failed Due Invalid Credentials.',
            error_code='VALIDATION_FAILED',
            error=serializer.errors,
        )


class LoginView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, *arg, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            tokens = TokenUtils.generate_tokens(serializer.validated_data['user'])
            TokenUtils.save_hash_token(tokens['refresh'])
            response = ResponseBuilder.success(
                message='Login Successful',
                detail={
                    "access_token": tokens['access'],
                }
            )
            CookieUtil.set_refresh_token(response, tokens['refresh'])
            return response
        return ResponseBuilder.error(
            message='Login Failed',
            error_code='INVALID_CREDENTIALS',
            error=serializer.errors
        )


class RefreshView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        refresh_token = CookieUtil.get_refresh_token(request)
        if not refresh_token:
            return ResponseBuilder.error(
                message='Refresh Failed',
                error_code='TOKEN_NOT_PROVIDED',
                error='No Refresh Token Provided',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        try:
            tokens = TokenUtils.rotate(refresh_token)
            response = ResponseBuilder.success(
                message='Refresh Successful',
                detail={
                    'access': tokens['access'],
                }
            )
            CookieUtil.set_refresh_token(response, tokens['refresh'])
            return response
        except TokenError as e:
            return ResponseBuilder.error(
                message='Refresh Failed',
                error_code='TOKEN_ERROR',
                error=str(e),
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = CookieUtil.get_refresh_token(request)
        if not refresh_token:
            return ResponseBuilder.error(
                message='Logout Failed',
                error_code='TOKEN_NOT_PROVIDED',
                error='No Token Provided',
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        try:
            TokenUtils.revoke_token(refresh_token)
        except TokenError as e:
            return ResponseBuilder.error(
                message='Logout Failed',
                error_code='TOKEN_ERROR',
                error=str(e),
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        response = ResponseBuilder.success(
            message='Logout Successful',
            detail=None,
        )
        CookieUtil.delete_refresh_token(response)
        return response

class Me(APIView):
    def get(self, request, *args, **kwargs):
        return ResponseBuilder.success(
            message='Me',
            detail='success',
        )