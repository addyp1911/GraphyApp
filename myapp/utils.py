from Graphy.settings import AWS_STORAGE_BUCKET_NAME
import boto3
from urllib.request import urlopen, Request
from PIL import Image as Img
from io import BytesIO
from .constants import headers

def upload_resized_images_to_S3(resized_image_key, in_mem_file):
    boto3.client("s3").upload_fileobj(
        in_mem_file, 
        Bucket=AWS_STORAGE_BUCKET_NAME,
        Key=resized_image_key,
        ExtraArgs={
            'ACL': 'public-read'
        }
    )
    resized_S3_image_url = boto3.client("s3").generate_presigned_url(
                        ClientMethod='get_object',
                        Params={
                            'Bucket':AWS_STORAGE_BUCKET_NAME,
                            'Key': resized_image_key
                        })
    return  resized_S3_image_url                   


def upload_resized_videos_to_S3(resized_key):
    resized_vid_key = ('resized_videos/{}').format(resized_key)
    with open(in_mem_file, 'rb') as data:
        boto3.client("s3").upload_fileobj(
            data, 
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=resized_vid_key,
            ExtraArgs={
                'ACL': 'public-read'
            }
        )
    resized_S3_url = boto3.client("s3").generate_presigned_url(
                        ClientMethod='get_object',
                        Params={
                            'Bucket':AWS_STORAGE_BUCKET_NAME,
                            'Key': resized_vid_key
                        })
    return resized_S3_vid_url

def retrieve_image(url):
    '''Download the image from the remote server''' 
    req = Request(url, headers=headers)
    return BytesIO(urlopen(req).read())

def resizing_image(story_id, story_obj, photo):
    image = Img.open(photo)
    resized_image = image.resize((600, 1200), Img.ANTIALIAS)
    in_mem_file = BytesIO()
    resized_image.save(in_mem_file, format='JPEG')
    in_mem_file.seek(0)
    resized_image_key = 'resized_images/{}.jpg'.format(str(story_id)+"_"+story_obj.grapher.username)
    resized_S3_image_url = upload_resized_images_to_S3(resized_image_key, in_mem_file)
    return resized_image, resized_S3_image_url

def resizing_video(story_id, story_obj, video_clip):
    resized_clip = video_clip.resize(width=480)
    resized_video_key = '{}.mp4'.format(str(story_id)+"_"+story_obj.grapher.username)
    resized_clip.write_videofile(resized_video_key, preset='ultrafast', remove_temp=True,
                        codec="libx264", audio = False, fps=30, logger=None, threads=4)
    resized_S3_video_url = upload_resized_videos_to_S3(resized_video_key)
    return resized_S3_video_url