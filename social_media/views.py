from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Post, Image, Like
from social_media.permissions import IsOwnerOrIsAuthenticatedReadAndCreateOrReadOnly
from social_media.serializers import (
    PostSerializer,
    PostListSerializer, PostUpdateSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrIsAuthenticatedReadAndCreateOrReadOnly,]
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action in ["retrieve", "create"]:
            return PostSerializer

        if self.action in ["update", "partial_update"]:
            return PostUpdateSerializer

    def get_queryset(self):
        queryset = Post.objects.all()

        if self.action == "list":
            queryset = queryset.select_related("author").annotate(
                likes_number=Count("likes")
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("images")

        return queryset

    @action(methods=["get"], detail=True, url_path="like-dislike", permission_classes=[IsAuthenticated])
    def like_dislike(self, request, pk=None):
        user = request.user
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            return Response({"detail": f"You liked {post} successfully"})
        if like:
            like.delete()
            return Response({"detail": f"You have successfully stopped liking {post}"})

    @action(methods=["get"], detail=True, url_path="like-dislike", permission_classes=[IsAuthenticated])
    def is_liked(self, request, pk=None):
        user = request.user
        post = self.get_object()
        if Like.objects.filter(user=user, post=post).exists():
            return Response({"is_liked": True})
        return Response({"is_liked": True})

