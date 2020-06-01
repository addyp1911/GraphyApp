from rest_framework import serializers
from .models import Story
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new registration
    """
    email = serializers.EmailField(label='Email Address', validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(label='password', max_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {"password":
                            {"write_only": True}
                        }

class StorySerializer(serializers.ModelSerializer):
    """
    A serializer defined for the model Story
    """
    photo = serializers.ImageField(allow_null=True,  allow_empty_file=True, required=False, max_length=None)
    video = serializers.FileField(allow_null=True, allow_empty_file=True, required=False, max_length=None)
    story_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Story  
        fields = ['photo', 'video','story_title','description','story_type','grapher','story_id']


class StoryModifySerializer(serializers.Serializer):
    """
    A serializer defined for modifying a Story feature
    """
    story_id =  serializers.CharField(max_length=25)

