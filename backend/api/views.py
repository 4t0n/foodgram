from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram_backend.constants import HOST_NAME
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, User
from users.models import Follow
from .serializers import (
    AvatarSerializers, FollowSerializer,
    GetLinkSerializer, IngredientSerializer, RecipeBaseSerializer,
    RecipeSerializer, RecipeCreateSerializer, SubscribeSerializer,
    TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination

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

    @action(['get'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            pagination_class=LimitOffsetPagination,
            )
    def subscriptions(self, request, *args, **kwargs):
        follows = request.user.subscriptions.all()
        page = self.paginate_queryset(follows)
        if page is not None:
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

    @action(['post'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/subscribe',
            )
    def subscribe(self, request, id=None, **kwargs):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if author == user:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        if author in user.subscriptions.all():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.create(user=user, author=author)
        serializer = SubscribeSerializer(
            author,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if author == user:
            return Response(
                {'errors': 'Нельзя отписаться от самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        if author not in user.subscriptions.all():
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(Follow, author=author, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateSerializer
        return self.serializer_class

    def update(self, request, *args, partial=True, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(['get',], detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = GetLinkSerializer(self.object)
        return Response({'short-link': f"{HOST_NAME}/s/"
                        f"{serializer.data.get('short_link')}"})

    @action(['post'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/favorite'
            )
    def favorite(self, request, id=None, **kwargs):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        if recipe in user.favorite.all():
            return Response(
                {'errors': 'Рецепт уже есть в избранном!'},
                status=status.HTTP_400_BAD_REQUEST)
        user.favorite.add(recipe)
        serializer = RecipeBaseSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        if recipe not in user.favorite.all():
            return Response(
                {'errors': 'Рецепт отсутствует в избранном!'},
                status=status.HTTP_400_BAD_REQUEST)
        user.favorite.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['post'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/shopping_cart'
            )
    def shopping_cart(self, request, id=None, **kwargs):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        if recipe in user.shopping_cart.all():
            return Response(
                {'errors': 'Рецепт уже есть в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.add(recipe)
        serializer = RecipeBaseSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, id=None):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        if recipe not in user.shopping_cart.all():
            return Response(
                {'errors': 'Рецепт отсутствует в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST)
        user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get',], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_cart = ''
        user = User.objects.get(id=1)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount', distinct=True))
        for ingredient in ingredients:
            shopping_cart += (
                f"— {ingredient['ingredient__name']}, "
                f"{ingredient['ingredient__measurement_unit']}\t"
                f"{ingredient['total']}\n"
            )
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=cart.txt'
        return response


class ShortLinkRedirect(RedirectView):
    permanent = False
    query_string = True
    pattern_name = "recipe-detail"

    def get(self, request, *args, **kwargs):
        object_url = kwargs['short_link']
        obj = get_object_or_404(Recipe, short_link=object_url)
        return redirect(obj.get_absolute_url())
