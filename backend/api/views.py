from django.contrib.auth import get_user_model
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, UserRegistrationSerializer, UserResetPasswordSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    # permission_classes = (IsAuthenticated)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'POST':
            serializer_class = UserRegistrationSerializer
        return serializer_class

    @action(detail=False, methods=('GET',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=('POST',),
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = UserResetPasswordSerializer(request.user)
        return Response(serializer.data)
