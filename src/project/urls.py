from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.views.i18n import set_language
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


admin.autodiscover()


@require_GET
def well_known_pki_validation(request):
    from django.http import HttpResponse
    return HttpResponse('503F265C7179F17AD100B8EFFBF476C0F480A41860D2F6ABA05F636411B75360 comodoca.com 66c77649d228b', content_type='text/plain')


urlpatterns = [
    path('.well-known/pki-validation/22694D944F9C631CF18B43DD25CCAE02.txt', well_known_pki_validation),
    path('choose-language', csrf_exempt(set_language), name='set_language'),
    path('login/', include('sa_login.urls')),
    path('admin/', admin.site.urls),
    path('', include('sa_web.urls')),
]

if settings.SHAREABOUTS['DATASET_ROOT'].startswith('/'):
    urlpatterns = [
        path('full-api/', include('sa_api_v2.urls')),
    ] + urlpatterns
