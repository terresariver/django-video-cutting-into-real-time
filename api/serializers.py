from rest_framework import serializers
from .models import Video

class VideoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id','titre','original','traite','status','date']
        extra_kwargs = {
            'titre':{'required':False}
        }
        
       