from rest_framework.generics import GenericAPIView
from .serializers import StorySerializer, RegisterSerializer, StoryModifySerializer
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status, filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from .models import *
from .tasks import async_task_for_resizing
import urllib, boto3
from Graphy.settings import AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID
from .utils import *
from moviepy.editor import VideoFileClip

def responsedata(status, message, data=None):
    if status:
        return {"status": status, "message": message, "data": data}
    else:
        return {"status": status, "message": message}


class RegisterView(GenericAPIView):
    """
     An endpoint for registering the user .
    """
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        :param request: POST request for registering a new user
        :return: returns user credentials to log into the account
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validated_data
            username = user_data['username']
            password = user_data['password']
            email = user_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            return Response(responsedata(True, "You are logged in successfully, go ahead and create your own story feature", user_data), status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(responsedata(False, "Something went wrong"), status=status.HTTP_400_BAD_REQUEST)

class StoryView(GenericAPIView):
    """
        :param request: POST
        :return: returns a success response when the story is successfully created or raises an exception in case of
                 errors with the request data
        :description: POST request to create a new story for a particular user
    """
    serializer_class = StorySerializer
    queryset = ""
    def post(self, request, *args, **kwargs):
        try:
            story_data = request.data.dict()
            serializer = StorySerializer(data=story_data, partial=True)
            grapher_name = story_data['grapher']
            current_user = User.objects.get(username=grapher_name)
            serializer.initial_data['grapher'] = current_user.pk
            if serializer.is_valid(raise_exception=True):
                serializer.save(grapher_id=current_user.pk) 
            photo = serializer.data.get('photo') if serializer.data.get('photo') else None
            video = serializer.data.get('video') if serializer.data.get('video') else None
            story_obj = Story.objects.get(pk=serializer.data.get('story_id'))
            story_obj.photo = photo
            story_obj.video = video
            story_obj.save()  
            # async_task_for_resizing.apply_async(args=[serializer.data, photo, video])
            return Response(responsedata(True, "A story feature is successfully created", serializer.data), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise ValidationError("The user matching query does not exist")
        except Exception as ex:
            return Response(responsedata(False, "Something went wrong"), status=status.HTTP_400_BAD_REQUEST)

class FetchStories(GenericAPIView):
    def get(self, request, *args, **kwargs):
        """
        :param request: GET
        :return: returns a success response when the stories are successfully fetched or raises an exception in case of
                errors with the function
        :description: GET request to fetch all the stories ordered by the newest first
        """
        try:
            params = request.GET
            stories_queryset = Story.objects.filter(status=0).order_by('-created_on')
            stories_list = []
            for story_det in stories_queryset:
                stories_list.append(story_det.as_dict())
            pagenumber = params.get('page', 1)
            paginator = Paginator(stories_list, 10)
            if int(pagenumber) > paginator.num_pages:
                raise ValidationError("Not enough pages", code=404)
            try:
                previous_page_number = paginator.page(pagenumber).previous_page_number()
            except EmptyPage:
                previous_page_number = None
            try:
                next_page_number = paginator.page(pagenumber).next_page_number()
            except EmptyPage:
                next_page_number = None
            return JsonResponse({'pagination': {
                'previous_page': previous_page_number,
                'is_previous_page': paginator.page(pagenumber).has_previous(),
                'next_page': next_page_number,
                'is_next_page': paginator.page(pagenumber).has_next(),
                'start_index': paginator.page(pagenumber).start_index(),
                'end_index': paginator.page(pagenumber).end_index(),
                'total_entries': paginator.count,
                'total_pages': paginator.num_pages,
                'page': int(pagenumber)
            },  'results': stories_list}, safe=False)
        except ValidationError as ex:
            return Response(responsedata(False, str(ex)))
        except Exception as ex:
            return Response(responsedata(False, "Something went wrong"), status=status.HTTP_400_BAD_REQUEST)

class ResizeStories(GenericAPIView):
    serializer_class = StoryModifySerializer
    def put(self, request, *args, **kwargs):
        """
        :param request: PUT
        :return: returns a success response when the stories are successfully resized to the desired dimensions or raises an exception in case of
                errors with the function
        :description: PUT request to upload all the resized stories and return the image/video URL of the resized resource in the response data, also 
                    add the resized resources to the story and save them in the database.
        """
        try:
            res_data = {}
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_data = serializer.data
            story_id = request_data.get('story_id')
            story_query_set = Story.objects.filter(pk=story_id)
            story_obj = Story.objects.get(pk=story_id)
            photo_url = story_query_set.values('photo')[0].get('photo')
            video_url = story_query_set.values('video')[0].get('video')
            if not photo_url and video_url:
                return Response(responsedata(True, "The story feature has no attached video or image"), status=status.HTTP_200_OK)
            if photo_url:
                image = retrieve_image(photo_url)
                resized_image, resized_S3_image_url = resizing_image(story_id, story_obj, image)
                res_data.update({'resized_image_dimensions': resized_image.size,'resized_image_url': resized_S3_image_url})
            if video_url:
                video_clip = VideoFileClip(video_url)
                resized_S3_video_url = resizing_video(story_id, story_obj, video_clip)
                res_data.update({{'resized_video_clip_dimensions': resized_clip.size,'resized_video_url': resized_S3_video_url}})                  
            return Response(responsedata(True, "The story feature has been successfully resized", res_data), status=status.HTTP_200_OK)
        except Exception as ex: 
            return Response(responsedata(False, "Something went wrong"), status=status.HTTP_400_BAD_REQUEST)