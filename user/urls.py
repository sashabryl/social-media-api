from django.urls import path
from rest_framework import routers

from user.views import CreateAuthToken, UserViewSet

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="user")

app_name = "user"

urlpatterns = [
    path("login", CreateAuthToken.as_view(), name="login")
]
