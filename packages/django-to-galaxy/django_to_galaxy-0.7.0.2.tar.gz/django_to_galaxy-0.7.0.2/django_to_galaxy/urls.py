from django.urls import include, path

urlpatterns = [path("api/", include("django_to_galaxy.api.urls"))]
