from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet)

api_urls = []

router_api = routers.DefaultRouter()
router_api.register('users', CustomUserViewSet, basename='user')
router_api.register('tags', TagViewSet, basename='tag')
router_api.register('ingredients', IngredientViewSet, basename='ingredient')
router_api.register('recipes', RecipeViewSet)

api_urls.extend(router_api.urls)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(api_urls)),
]
