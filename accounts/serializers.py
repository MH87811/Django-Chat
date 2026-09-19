from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'n_code', 'password', 'password2', 'type', 'company_name', 'country_code', 'state_code', 'city', 'address', 'zip_code')

        extra_kwargs = {
            "password": {
                'write_only': True
            },
            "password2": {
                'write_only': True
            }
        }

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email Already Taken.')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone Number Already Taken.')

        if not re.fullmatch(r'^9\d{9}$', value):
            raise serializers.ValidationError('Invalid Phone Number.')

        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=r'^9\d{9}$', error_messages={
        "invalid": "Invalid Phone Number",
    })
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        user = authenticate(phone=phone, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid Credentials.')
        attrs['user'] = user
        return attrs