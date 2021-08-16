from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in

from soci3LApp.models import UserInfo, BlockedBy


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('id', 'email', 'first_name',
                  'last_name', 'pseudo_name', 'image')


class UsrSrlzrForOthers(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('first_name', 'last_name', 'pseudo_name')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('email', 'password')

    def create(self, validated_data):
        user = UserInfo.objects.create_user(
            self.validated_data['email'],
            self.validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            user.isLoggedIn = True
            user.save(update_fields=['isLoggedIn'])
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = (
            'id',
            'pseudo_name',
            'first_name',
            'last_name',
            'last_login',
            'isLoggedIn',
            'gender',
            'date_joined',
            'image',
            'socialImageUrl',
        )


class ggPlusSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class friendSrlzr(serializers.Serializer):
    friendId = serializers.IntegerField()


class friendRqstSrlzr(serializers.Serializer):
    friendId = serializers.IntegerField()
    friendship = serializers.CharField()



