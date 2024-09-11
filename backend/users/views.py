from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.permissions import CurrentUserOrAdmin
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet

from .serializers import AvatarSerializers

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)
    # lookup_field = 'username'
    # permission_classes = (IsAuthenticated)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(['get',], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['put',],
        detail=False,
        permission_classes=(CurrentUserOrAdmin,),
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        serializer = AvatarSerializers(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self.request.user
        user.avatar.delete()
        user.save
        return Response(status=status.HTTP_204_NO_CONTENT)
