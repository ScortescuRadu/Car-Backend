from rest_framework import serializers
import re
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password']

    def validate_password(self, value):
        # Add your password validation logic here
        min_length = 8
        special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
        
        if len(value) < min_length:
            raise serializers.ValidationError(f"Password must be at least {min_length} characters long.")

        if not any(char in special_characters for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate_username(self, value):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not re.match(email_regex, value):
            raise serializers.ValidationError("Username must have an email structure.")

        return value

    def create(self, validated_data):
        username = validated_data.get('username', None)
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class TokenInputSerializer(serializers.Serializer):
    token = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    pass
