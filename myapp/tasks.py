from celery import shared_task
from .utils import *
from django.core.mail import send_mail
from smtplib import SMTPException
from Graphy.settings import EMAIL_HOST_USER
import os
from django.core.files import File

@shared_task(name='async_task_for_resizing')
def async_task_for_resizing(story_data, photo, video):
    try:
        resized_S3_video_url, resized_S3_image_url = None, None
        story_id = story_data.get('story_id')
        story_obj = Story.objects.get(pk=story_id)
        if photo:
            image = retrieve_image(photo)
            resized_S3_image_url = resizing_image(story_id, story_obj, image)
        if video:
            resized_S3_video_url = resizing_video(story_id, story_obj, video_clip)   
    except Exception as e:
        return Response({'Error':'Something went wrong'})               