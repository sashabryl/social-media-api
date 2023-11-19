from rest_framework import serializers

from social_media.models import Image, Post


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("image",)


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(max_length=100000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )

    class Meta:
        model = Post
        fields = ("author", "title", "contend", "images", "upload_images")

    def create(self, validated_data):
        images_data = validated_data.pop("upload_images", [])
        post = Post.objects.create(**validated_data)

        for image_data in images_data:
            Image.objects.create(post=post, image=image_data)

        return post


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "author", "created_at")
