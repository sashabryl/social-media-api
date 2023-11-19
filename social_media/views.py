from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser

from social_media.models import Post, Image
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()

        if self.action == "list":
            queryset = queryset.select_related("author")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("images")

        return queryset
