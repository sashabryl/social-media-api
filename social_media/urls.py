from django.urls import path, include
from rest_framework import routers

from social_media.views import PostViewSet

app_name = "social-media"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")


urlpatterns = [path("", include(router.urls))]
