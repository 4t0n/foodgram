from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet

user_urls = []

router_users = routers.DefaultRouter()
router_users.register('users', CustomUserViewSet, basename='user')
user_urls.extend(router_users.urls)

urlpatterns = [
    path('', include(user_urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('', include(api_urls)),
]
