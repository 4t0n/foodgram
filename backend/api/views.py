from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram_backend.constants import HOST_NAME
from recipes.models import Ingredient, Recipe, Tag
from .serializers import (
    GetLinkSerializer, IngredientSerializer, RecipeSerializer,
    RecipeCreateSerializer, TagSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
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


class ShortLinkRedirect(RedirectView):
    permanent = False
    query_string = True
    pattern_name = "recipe-detail"

    def get(self, request, *args, **kwargs):
        object_url = kwargs['short_link']
        obj = get_object_or_404(Recipe, short_link=object_url)
        return redirect(obj.get_absolute_url())
