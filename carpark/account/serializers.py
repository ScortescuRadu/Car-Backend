from rest_framework import serializers
from .models import User, UserInfo

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        # Add your password validation logic here
        min_length = 8
        special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/"
        
        if len(value) < min_length:
            raise serializers.ValidationError(f"Password must be at least {min_length} characters long.")

        if not any(char in special_characters for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class LoginResponseSerializer(serializers.Serializer):
    jwt = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    pass

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'