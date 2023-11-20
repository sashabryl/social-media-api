from django.db.models import Count, Q
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Post, Like, Tag
from social_media.permissions import IsOwnerOrReadCreateOrReadOnly
from social_media.serializers import (
    PostListSerializer,
    PostUpdateSerializer,
    TagSerializer, PostCreateSerializer, PostDetailSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadCreateOrReadOnly]
    parser_classes = [MultiPartParser]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "create":
            return PostCreateSerializer

        if self.action in ["update", "partial_update"]:
            return PostUpdateSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

    def get_queryset(self):
        """Filter by case-insensitive title or list of case-insensitive names of tags"""

        queryset = Post.objects.all()

        title = self.request.query_params.get("title")
        tags_str = self.request.query_params.get("tags")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if tags_str:
            tags = tags_str.split(",")
            tag_filters = Q()
            for tag in tags:
                tag_filters |= Q(tags__name__icontains=tag.strip())
            queryset = queryset.filter(tag_filters)

        if self.action == "list":
            queryset = queryset.select_related("author").prefetch_related("tags").annotate(
                likes_number=Count("likes")
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("images", "tags").annotate(
                likes_number=Count("likes")
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["get"],
        detail=True,
        url_path="like-dislike",
        permission_classes=[IsAuthenticated],
    )
    def like_dislike(self, request, pk=None):
        user = request.user
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            return Response({"detail": f"You liked {post} successfully"})
        if like:
            like.delete()
            return Response(
                {"detail": f"You have successfully stopped liking {post}"}
            )

    @action(
        methods=["get"],
        detail=True,
        url_path="is-liked",
        permission_classes=[IsAuthenticated],
    )
    def is_liked(self, request, pk=None):
        user = request.user
        post = self.get_object()
        if Like.objects.filter(user=user, post=post).exists():
            return Response({"is_liked": True})
        return Response({"is_liked": False})


class TagCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
