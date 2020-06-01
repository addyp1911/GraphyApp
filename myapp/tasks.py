from celery import shared_task
from .utils import *
from django.core.mail import send_mail
from smtplib import SMTPException
from Graphy.settings import EMAIL_HOST_USER

@shared_task(name='async_task_for_resizing',bind=True, default_retry_delay=60, max_retries=2)
def async_task_for_resizing(self, story_data, photo, video):
    try:
        resized_S3_video_url, resized_S3_image_url = None, None
        story_id = story_data.get('story_id')
        story_obj = Story.objects.get(pk=story_id)
        if photo:
            image = retrieve_image(photo)
            resized_S3_image_url = resizing_image(story_id, story_obj, image)
        if video:
            resized_S3_video_url = resizing_video(story_id, story_obj, video_clip)
        if resized_S3_image_url or resized_S3_video_url:  
            subject = "Mail notification for your resized resources of your story feature"
            body = "Your image url is: "+ str(resized_S3_image_url) + "Your video url is: " + str(resized_S3_video_url)
            FROM = EMAIL_HOST_USER
            email_id = story_obj.grapher.email
            recipient = [email_id] 
            mail_status = send_mail(subject, body, FROM, recipient,
                    fail_silently=False)
    except SMTPException as e:
        raise self.retry(exc=e)                