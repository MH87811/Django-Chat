from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST


class ResponseBuilder:
    @staticmethod
    def success(message, detail, status_code=status.HTTP_200_OK):
        return Response({
            'message': message,
            'detail': detail,
        }, status=status_code)

    @staticmethod
    def error(message, error_code, error, status_code=HTTP_400_BAD_REQUEST):
        return Response({
            "message": message,
            "error_code": error_code,
            "error": error,
        }, status=status_code)
    
    @classmethod
    def internal_server_error(cls, exception):
        return cls.error(
            message='Internal Server Error',
            error_code='INTERNAL_SERVER_ERROR',
            error=str(exception),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @classmethod
    def not_found_error(cls, obj):
        return cls.error(
            message=f'{obj} Not Found.',
            error_code='NOT_FOUND',
            status_code=status.HTTP_404_NOT_FOUND,
        )