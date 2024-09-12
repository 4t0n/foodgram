from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

api_urls = []

router_api = routers.DefaultRouter()
router_api.register('tags', TagViewSet, basename='tag')
router_api.register('ingredients', IngredientViewSet, basename='ingredient')
router_api.register('recipes', RecipeViewSet, basename='recipe')
api_urls.extend(router_api.urls)

urlpatterns = [
    path('', include('users.urls')),
    path('', include(api_urls)),
]
