from rest_framework import status
from rest_framework.response import Response


def post_destroy_mixin(
        obj, field, request, serializer, error_message_post,
        error_message_destroy):
    """Создаёт или удаляет записи в БД."""
    if obj in field.all():
        if request.method == 'POST':
            return Response(
                {'errors': error_message_post},
                status=status.HTTP_400_BAD_REQUEST)
        field.remove(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == 'POST':
        field.add(obj)
        serializer = serializer(obj, context={"request": request},)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)
    return Response(
        {'errors': error_message_destroy},
        status=status.HTTP_400_BAD_REQUEST)
