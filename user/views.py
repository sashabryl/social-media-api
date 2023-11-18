from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Follow
from user.permissions import IsOwnerOrReadOnly, IsNotOwner
from user.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserPictureSerializer,
    FollowSerializer,
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

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"] or (
            self.action == "my_profile"
            and self.request.method in ["PUT", "PATCH"]
        ):
            return UserUpdateSerializer

        if self.action in ["retrieve"] or (
            self.action == "my_profile" and self.request.method == "GET"
        ):
            return UserDetailSerializer

        if self.action == "change_password":
            return UserChangePasswordSerializer

        if self.action == "upload_avatar":
            return UserPictureSerializer

        if self.action == "list":
            return UserListSerializer

        if self.action == "follow":
            return FollowSerializer

    @action(
        methods=["GET", "PUT", "PATCH"],
        detail=False,
        url_path="me",
    )
    def my_profile(self, request):
        if request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        if request.method == "GET":
            serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path="me-upload-avatar")
    def upload_avatar(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="follow",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def follow(self, request, pk=None):
        follower = request.user
        followed = self.get_object()
        serializer = self.get_serializer(
            data={"follower": follower.id, "followed": followed.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": f"Now you follow {followed.email}!"})

    @action(
        methods=["POST"],
        detail=False,
        url_path="change-password",
    )
    def change_password(self, request):
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


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []
    authentication_classes = []
