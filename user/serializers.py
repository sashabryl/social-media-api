from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from django.core import exceptions


class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            },
            "first_name": {
                "required": False,
                "style": {"placeholder": "optional"},
            },
            "last_name": {
                "required": False,
                "style": {"placeholder": "optional"},
            },
        }

    @staticmethod
    def validate_password(value):
        try:
            validate_password(value)
        except exceptions.ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate(self, data):
        if data.get("password") != data.pop("password_confirm"):
            raise ValidationError(
                "Passwords do not match. Make sure you enter the same passwords"
            )
        return super().validate(data)

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True)
    following = serializers.StringRelatedField(many=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "picture",
            "first_name",
            "last_name",
            "email",
            "bio",
            "followers",
            "following",
        )


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email", "picture")


class UserPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "picture")


class UserUpdateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "bio",
        )
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "bio": {"required": False},
        }


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        max_length=255,
        style={
            "input_type": "password",
            "placeholder": "Your old password password",
        },
    )
    password = serializers.CharField(
        required=True,
        max_length=255,
        style={"input_type": "password", "placeholder": "New password"},
    )
    confirmed_password = serializers.CharField(
        required=True,
        max_length=255,
        style={"input_type": "password", "placeholder": "Repeat"},
    )

    def validate(self, data):
        if not data.get("password") == data.get("confirmed_password"):
            raise ValidationError(
                "Confirm your new password carefully (they don't match)"
            )
        try:
            validate_password(data.get("password"))
        except exceptions.ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return super().validate(data)
