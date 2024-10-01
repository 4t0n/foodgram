from rest_framework import status
from rest_framework.response import Response


class PostDestroyMixin:
    """Создание и удаление записей в БД."""

    def add_object(self, data, serializer_class):
        serializer = serializer_class(
            data=data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy_object(self, obj, related_manager):
        if related_manager.filter(id=obj.id).exists():
            related_manager.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
