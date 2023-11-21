from celery import shared_task
from django.contrib.auth import get_user_model

from social_media.models import Post, Image


@shared_task
def create_scheduled_post(author_id, title, contend, tags, images_data):
    author = get_user_model().get(id=author_id)
    post = Post.objects.create(author=author, title=title, contend=contend)
    if tags:
        post.tags.set(tags)
        post.save()

    for image in images_data:
        Image.objects.create(post=post, image=image)
