from rest_framework import serializers
from .models import CustomUser
from django.utils.timezone import localtime
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    referral_id = serializers.CharField(required=False)
    registration_timestamp = serializers.SerializerMethodField()

    def get_registration_timestamp(self, obj):
        created_time = localtime(obj.timestamp)
        return created_time.strftime("%I:%M:%S, %dth %B, %Y")

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST' and 'register' in request.path:
            return data

    class Meta:
        model = CustomUser
        fields = ['user_id', 'name', 'email', 'password', 'referral_id', 'referral_code', 'points', 'registration_timestamp']

