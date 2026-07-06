from rest_framework import serializers
from .models import Video,Watermark,User

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','username']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type':'password'})
    password2 = serializers.CharField(write_only=True,required=True,style={'input_type':'password'})

    class Meta:
        model = User
        fields = ['email','password','password2']

    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password":"Les mots de passe ne correspondent pas"})
        return data

    def create(self,validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        email = validated_data['email']
        username = email.replace('@','_').replace('.','_')   #tom@gmail.com devient tom_gmail_com
        user = User.objects.create_user(
            email=email,
            password= password,
            username=username
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,style={'input_type':'password'})
       