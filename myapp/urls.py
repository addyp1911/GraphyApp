from django.contrib import admin
from django.urls import path, include
from .views import StoryView, FetchStories, ResizeStories, RegisterView

urlpatterns = [
    path('register_user/', RegisterView.as_view(), name="register-user"),
    path('create_story/', StoryView.as_view(), name="create-story"),
    path('fetch_stories/', FetchStories.as_view(), name="fetch-stories"),
    path('resize_story/', ResizeStories.as_view(), name="resize-story"),
]
