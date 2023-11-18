from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin, UpdateModelMixin)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.serializers import UserSerializer, UserUpdateSerializer, UserChangePasswordSerializer


class UserViewSet(
    viewsets.GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin
):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer

        return UserSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserChangePasswordView(generics.UpdateAPIView):
    serializer_class = UserChangePasswordSerializer
    model = get_user_model()
    permission_classes = [IsAuthenticated,]

    def get_object(self):
        return self.request.user

