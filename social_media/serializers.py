from rest_framework import serializers

from social_media.models import Image, Post, Like, Tag


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)


class PostCreateSerializer(serializers.ModelSerializer):
    upload_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=100000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "contend",
            "tags",
            "upload_images",
        )

    def create(self, validated_data):
        images_data = validated_data.pop("upload_images", [])
        tags = validated_data.pop("tags", [])
        post = Post.objects.create(**validated_data)

        if tags:
            post.tags.set(tags)
            post.save()

        for image_data in images_data:
            Image.objects.create(post=post, image=image_data)

        return post


class PostDetailSerializer(serializers.ModelSerializer):
    likes_number = serializers.IntegerField(read_only=True)
    tags = serializers.StringRelatedField(many=True)
    images = ImageSerializer(many=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "likes_number",
            "images",
            "contend",
            "tags",
            "created_at"
        )


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("contend", "tags")

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", [])
        if tags:
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class PostListSerializer(serializers.ModelSerializer):
    likes_number = serializers.IntegerField()
    author = serializers.StringRelatedField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "tags",
            "created_at",
            "likes_number",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
