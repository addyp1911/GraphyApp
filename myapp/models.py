from django.db import models
from django.contrib.auth.models import User 

class BasicDetails(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=0)
    class Meta:
        abstract = True
 
 
class Story(BasicDetails):
    story_id  = models.AutoField(primary_key=True)
    grapher = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    story_title = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    duration = models.TimeField(blank=True, null=True)
    story_type = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)

    def __str__(self):
        return  self.grapher.username + "_" + str(self.story_id)

    def as_dict(self):
        story_details_dict = {
            'story_id': self.story_id,
            'grapher_name': self.grapher.username,
            'story_title': self.story_title,
            'description': self.description,
            'duration': self.duration,
            'story_type': self.story_type,
            'photo': str(self.photo),
            'video': str(self.video),
            'created_on': self.created_on,
        }
        return story_details_dict
