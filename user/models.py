import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


def user_picture_file_path(instance, filename) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.picture)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    bio = models.TextField()
    picture = models.ImageField(
        upload_to=user_picture_file_path,
        null=True,
        blank=True
    )
    followers = models.ManyToManyField("self", related_name="following")

