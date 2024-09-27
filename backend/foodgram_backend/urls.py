from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from api.views import ShortLinkRedirect

urlpatterns = [
    path(
        'about/',
        TemplateView.as_view(template_name='about.html'),
        name='about',
    ),
    path(
        'technologies/',
        TemplateView.as_view(template_name='technologies.html'),
        name='technologies',
    ),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', ShortLinkRedirect.as_view()),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc',
    ),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
