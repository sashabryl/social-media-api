from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView, TokenBlacklistView,
)

from user.views import UserViewSet

router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="user")

app_name = "user"

urlpatterns = [
    path(
        "login/", TokenObtainPairView.as_view(), name="login"
    ),
    path(
        "token-refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("token-verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("logout/", TokenBlacklistView.as_view(), name="logout")
]
