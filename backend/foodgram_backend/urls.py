from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from api.views import CustomUserViewSet, ShortLinkRedirect

user_urls = []

router_users = routers.DefaultRouter()
router_users.register('users', CustomUserViewSet, basename='user')
user_urls.extend(router_users.urls)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', ShortLinkRedirect.as_view()),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
