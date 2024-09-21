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

from foodgram_backend.constants import HOST_NAME
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, User
from .filters import IngredientFilter, RecipeFilter
from .mixins import post_destroy_mixin
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (
    AvatarSerializers, FollowSerializer,
    GetLinkSerializer, IngredientSerializer, RecipeBaseSerializer,
    RecipeSerializer, RecipeCreateSerializer, TagSerializer,
)


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination

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
            )
    def subscriptions(self, request, *args, **kwargs):
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

    @action(['post', 'delete'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/subscribe',
            )
    def subscribe(self, request, id=None, **kwargs):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if author == user:
            return Response(
                {'errors': 'Нельзя иметь подписку на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        return post_destroy_mixin(
            obj=author,
            field=user.subscriptions,
            request=request,
            serializer=FollowSerializer,
            error_message_post='Вы уже подписаны на этого пользователя!',
            error_message_destroy='Вы не подписаны на этого пользователя!',
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPageNumberPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

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

    def update(self, request, *args, partial=True, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(['get',], detail=True, url_path='get-link')
    def get_link(self, request, *args, **kwargs):
        serializer = GetLinkSerializer(self.get_object())
        return Response({'short-link': f"{HOST_NAME}/s/"
                        f"{serializer.data.get('short_link')}"})

    @action(['post', 'delete'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/favorite'
            )
    def favorite(self, request, id=None, **kwargs):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        return post_destroy_mixin(
            obj=recipe,
            field=user.favorite,
            request=request,
            serializer=RecipeBaseSerializer,
            error_message_post='Рецепт уже есть в избранном!',
            error_message_destroy='Рецепт отсутствует в избранном!',
        )

    @action(['post', 'delete'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path=r'(?P<id>\d+)/shopping_cart'
            )
    def shopping_cart(self, request, id=None, **kwargs):
        recipe = get_object_or_404(Recipe, pk=id)
        user = request.user
        return post_destroy_mixin(
            obj=recipe,
            field=user.shopping_cart,
            request=request,
            serializer=RecipeBaseSerializer,
            error_message_post='Рецепт уже есть в списке покупок!',
            error_message_destroy='Рецепт отсутствует в списке покупок!',
        )

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
