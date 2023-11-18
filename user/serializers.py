from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "bio",
        )
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "bio": {"required": False},
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


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
    old_password = serializers.CharField(required=True, max_length=30)
    password = serializers.CharField(required=True, max_length=30)
    confirmed_password = serializers.CharField(
        required=True, max_length=30
    )

    def validate(self, data):
        if not self.context["request"].user.check_password(
            data.get("old_password")
        ):
            raise serializers.ValidationError(
                {"old_password": "Wrong password."}
            )

        if data.get("confirmed_password") != data.get("password"):
            raise serializers.ValidationError(
                {"password": "Password must be confirmed correctly."}
            )

        return data

    def update(self, instance, validated_data):
        validate_password(validated_data.get("password"))
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    @property
    def data(self):
        return {"Success": True}
