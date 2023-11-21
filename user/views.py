from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response


from user.models import Follow
from user.permissions import IsOwnerOrReadOnly, IsNotOwner
from user.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserPictureSerializer,
)


class UserViewSet(
    viewsets.GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
):
    serializer_class = UserListSerializer
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        email = self.request.query_params.get("email")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if email:
            queryset = queryset.filter(email__icontains=email)

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if self.action in ["retrieve", "is_followed", "my_profile"]:
            queryset = queryset.prefetch_related(
                "followers__follower", "following__followed", "posts__images"
            )

        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"] or (
            self.action == "my_profile"
            and self.request.method in ["PUT", "PATCH"]
        ):
            return UserUpdateSerializer

        if self.action == "retrieve" or (
            self.action == "my_profile" and self.request.method == "GET"
        ):
            return UserDetailSerializer

        if self.action == "change_password":
            return UserChangePasswordSerializer

        if self.action == "upload_avatar":
            return UserPictureSerializer

        if self.action == "list":
            return UserListSerializer

    @extend_schema(
        request=UserDetailSerializer,
        methods=["POST"]
    )
    @action(
        methods=["GET", "PUT", "PATCH"],
        detail=False,
        url_path="me",
    )
    def my_profile(self, request):
        """Returns the client's detail page with ability to update it"""
        if request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if request.method == "GET":
            serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    @extend_schema(
        request=UserPictureSerializer,
        methods=["POST"]
    )
    @action(methods=["POST"], detail=False, url_path="me-upload-avatar")
    def upload_avatar(self, request):
        """Uploads or changes the client's avatar"""
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="follow-unfollow",
        permission_classes=[
            IsNotOwner,
        ],
    )
    def follow_unfollow(self, request, pk=None):
        """
        Creates a Follow instance where the follower is the client
        and the followed is the profile's owner if there is no such Follow instance, and
        deletes it otherwise.
        """
        follower = request.user
        followed = self.get_object()
        follow, created = Follow.objects.get_or_create(
            follower=follower, followed=followed
        )
        if created:
            return Response({"detail": f"Now you follow {followed.email}!"})
        follow.delete()
        return Response({"detail": f"Now you don't follow {followed.email}"})

    @action(
        methods=["GET"],
        detail=True,
        url_path="is-followed",
        permission_classes=[IsNotOwner],
    )
    def is_followed(self, request, pk=None):
        """Checks if the client is following a specific user"""
        follower = request.user
        followed = self.get_object()
        is_followed = Follow.objects.filter(
            followed=followed, follower=follower
        ).exists()
        return Response({"detail": {"is_followed": is_followed}})

    @extend_schema(
        request=UserChangePasswordSerializer,
        methods=["POST"]
    )
    @action(
        methods=["POST"],
        detail=False,
        url_path="change-password",
    )
    def change_password(self, request):
        """Changes the client's password or raises ValidationErrors"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.data.get("old_password")
        new_password = serializer.data.get("password")

        if not user.check_password(old_password):
            raise ValidationError("Old password is incorrect")

        user.set_password(new_password)
        user.save()
        return Response(data={"Success": True})

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                description="Filter by case-insensitive email (ex. ?email=sasha)",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter by case-insensitive first_name (ex. ?first_name=sasha)",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter by case-insensitive last_name (ex. ?last_name=sasha)",
                required=False,
                type=str
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []
    authentication_classes = []
