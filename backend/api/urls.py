from django.urls import include, path
from rest_framework import routers

from .views import (
    FoodgramUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

api_urls = []
v1_router_api = routers.DefaultRouter()
v1_router_api.register('users', FoodgramUserViewSet, basename='user')
v1_router_api.register('tags', TagViewSet, basename='tag')
v1_router_api.register('ingredients', IngredientViewSet, basename='ingredient')
v1_router_api.register('recipes', RecipeViewSet, basename='recipes')

api_urls.extend(v1_router_api.urls)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(api_urls)),
]
