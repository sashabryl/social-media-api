import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{instance.post}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/images", filename)


class Image(models.Model):
    image = models.ImageField(upload_to=image_file_path)
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True
    )


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="likes"
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=("user", "post"), name="unique_like")
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    contend = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

