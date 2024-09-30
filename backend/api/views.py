import os

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from django_filters.rest_framework import DjangoFilterBackend
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag, User

from .filters import IngredientFilter, RecipeFilter
from .mixins import PostDestroyMixin
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (
    AvatarSerializers,
    CreateFavoriteSerializer,
    CreateShoppingSerializer,
    CreateSubscribeSerializer,
    FollowSerializer,
    GetLinkSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    TagSerializer,
)


class FoodgramUserViewSet(UserViewSet, PostDestroyMixin):
    """Вьюсет для работы с пользователями."""

    pagination_class = CustomPageNumberPagination

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(['get'], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        """Выводит информацию об авторизованном пользователе."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['put'],
        detail=False,
        permission_classes=(CurrentUserOrAdmin,),
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        """Добавляет аватар пользователя."""
        serializer = AvatarSerializers(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        """Удаляет аватар пользователя."""
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request, *args, **kwargs):
        """Выводит информацию о подписках пользователей."""
        follows = request.user.subscriptions.all()
        page = self.paginate_queryset(follows)
        if page:
            serializer = FollowSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            follows,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    @action(
        ['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<id>\d+)/subscribe',
    )
    def subscribe(self, request, id=None, **kwargs):
        """Добавляет подписку."""
        data = {
            'author': get_object_or_404(User, pk=id).id,
            'user': request.user.id,
        }
        return self.add_object(data, CreateSubscribeSerializer)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None, **kwargs):
        """Удаляет подписку пользователя."""
        return self.destroy_object(
            get_object_or_404(User, pk=id), self.request.user.subscriptions
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet, PostDestroyMixin):
    """Вьюсет для работы с рецептами."""

    pagination_class = CustomPageNumberPagination
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.annotated_fields(self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ('partial_update', 'destroy'):
            self.permission_classes = [IsAuthorOrAdmin]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return self.serializer_class

    @action(['get'], detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        """Выводит короткую ссылку на текущий рецепт."""
        serializer = GetLinkSerializer(self.get_object())
        return Response(
            {
                'short-link': f"{os.getenv('HOST_NAME')}/s/"
                f"{serializer.data.get('short_link')}/"
            }
        )

    @action(
        ['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<id>\d+)/favorite',
    )
    def favorite(self, request, id=None, **kwargs):
        """Реализует добавление рецептов в избранное."""
        data = {
            'recipe': get_object_or_404(Recipe, pk=id).id,
            'user': request.user.id,
        }
        return self.add_object(data, CreateFavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, id=None, **kwargs):
        """Удаляет подписку пользователя."""
        return self.destroy_object(
            get_object_or_404(Recipe, pk=id), self.request.user.favorites
        )

    @action(
        ['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path=r'(?P<id>\d+)/shopping_cart',
    )
    def shopping_cart(self, request, id=None, **kwargs):
        """Реализует добавление рецептов в избранное."""
        data = {
            'recipe': get_object_or_404(Recipe, pk=id).id,
            'user': request.user.id,
        }
        return self.add_object(data, CreateShoppingSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, id=None, **kwargs):
        """Удаляет подписку пользователя."""
        return self.destroy_object(
            get_object_or_404(Recipe, pk=id), self.request.user.shopping_cart
        )

    @action(['get'], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        """Загрузка списка покупок."""
        shopping_cart = ''
        user = request.user
        ingredients = (
            Ingredient.objects.filter(
                ingredient_to_recipe__recipe__shopping=user
            )
            .annotate(total_amount=Sum('ingredient_to_recipe__amount'))
            .values('name', 'measurement_unit', 'total_amount')
            .order_by('name')
        )
        for ingredient in ingredients:
            shopping_cart += (
                f"— {ingredient['name']}, "
                f"{ingredient['measurement_unit']}\t"
                f"{ingredient['total_amount']}\n"
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment;filename={user.username}-cart.txt'
        )
        return response


class ShortLinkRedirect(RedirectView):
    """Вьюсет для перенаправления с короткой ссылки."""

    permanent = False
    query_string = True
    pattern_name = "recipe-detail"

    def get(self, request, *args, **kwargs):
        object_url = kwargs['short_link']
        obj = get_object_or_404(Recipe, short_link=object_url)
        return redirect(f"{os.getenv('HOST_NAME')}{obj.get_absolute_url()}")
