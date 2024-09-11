from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    ...
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    # lookup_field = 'username'
    # permission_classes = (IsAuthenticated)

