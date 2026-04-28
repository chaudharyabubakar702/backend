from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

urlpatterns = [
    path("", lambda x: HttpResponse("Backend is running!")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("dispatch.urls")),
    # Silence favicon.ico 404 logs
    path("favicon.ico", lambda x: HttpResponse(status=204)),
]
