from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views

from .views import CheckImei

app_name = "api"
urlpatterns = [
    path("check-imei", CheckImei.as_view(), name="imei_check"),
    path("api-token-auth/", views.obtain_auth_token),
]

urlpatterns = format_suffix_patterns(urlpatterns)
