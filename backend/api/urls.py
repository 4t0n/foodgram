from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet

api_urls = []

router_api = routers.DefaultRouter()
# router_api.register('users', UserViewSet, basename='user')

api_urls.extend(router_api.urls)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    # path('', include(api_urls)),
]
