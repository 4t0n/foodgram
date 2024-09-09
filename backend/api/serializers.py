from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )

class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password', )



# class UserWithPasswordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'password',
#         )


class UserResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=128)
    current_password = serializers.CharField(max_length=128)
