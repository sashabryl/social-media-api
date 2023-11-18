from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.mixins import (ListModelMixin, RetrieveModelMixin, UpdateModelMixin)

from user.serializers import UserSerializer


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


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


