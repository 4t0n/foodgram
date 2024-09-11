from django.urls import include, path
from rest_framework import routers

api_urls = []

router_api = routers.DefaultRouter()

api_urls.extend(router_api.urls)

urlpatterns = [
    path('', include('users.urls')),
]
