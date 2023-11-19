from rest_framework import serializers

from social_media.models import Image, Post


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "image")


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(required=False, many=True)

    class Meta:
        model = Post
        fields = ("id", "title", "author", "content", "images", "created_at")

    def create(self, validated_data):
        images = validated_data.pop("images")
        post = Post.objects.create(**validated_data)
        for image in images:
            Image.objects.create(post=post, **image)
        return post


