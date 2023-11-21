from rest_framework import serializers

from social_media.models import Image, Post, Like, Tag, Comment
from social_media.tasks import create_scheduled_post


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "contend")


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ("author", "contend", "created_at")


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
    scheduled_time = serializers.DateTimeField(write_only=True, default=None)

    class Meta:
        model = Post
        fields = (
            "title",
            "contend",
            "tags",
            "upload_images",
            "scheduled_time",
        )

    def create(self, validated_data):
        scheduled_time = validated_data.pop("scheduled_time", None)
        if scheduled_time:
            author_id = validated_data.get("author").id
            title = validated_data.get("title")
            contend = validated_data.get("contend")
            tags = validated_data.get("tags")
            images_data = validated_data.get("upload_images")
            create_scheduled_post.delay(
                author_id, title, contend, tags, images_data
            )
            return validated_data
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
    comments = CommentListSerializer(many=True, read_only=True)

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
            "comments",
            "created_at",
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
    comments_number = serializers.IntegerField()
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
            "comments_number",
            "likes_number",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class PostProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "images", "created_at")
