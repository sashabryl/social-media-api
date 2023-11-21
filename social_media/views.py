from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Post, Like, Tag
from social_media.permissions import IsOwnerOrReadCreateOrReadOnly
from social_media.serializers import (
    PostListSerializer,
    PostUpdateSerializer,
    TagSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    CommentCreateSerializer,
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

        if self.action == "add_comment":
            return CommentCreateSerializer

    def get_queryset(self):
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
            queryset = (
                queryset.select_related("author")
                .prefetch_related("tags")
                .annotate(
                    likes_number=Count("likes"),
                    comments_number=Count("comments"),
                )
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "images", "tags", "comments__author"
            ).annotate(likes_number=Count("likes"))

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
        """Creates a Like instance if there isn't one and deletes it otherwise"""
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
        """Checks if the client likes the post"""
        user = request.user
        post = self.get_object()
        if Like.objects.filter(user=user, post=post).exists():
            return Response({"is_liked": True})
        return Response({"is_liked": False})

    @extend_schema(request=CommentCreateSerializer, methods=["POSt"])
    @action(
        methods=["POST"],
        detail=True,
        url_path="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        author = request.user
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by case-insensitive title (ex. ?title=islam as cultural catalyst)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="tags",
                description="Filter by a list or case-insensitive tags (ex. ?tags=barby,fishing)",
                required=False,
                type={"list": {"items": {"type": "str"}}},
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TagCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
