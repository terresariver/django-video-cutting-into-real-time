from rest_framework import serializers
from .models import Video,Watermark

class VideoSerializer (serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id','titre','original','traite','thumbnail','status','date']
        extra_kwargs = {
            'titre':{'required':False}
        }

class WatermarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watermark
        fields = ['id','image']
       