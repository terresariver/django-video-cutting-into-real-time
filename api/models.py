from django.db import models
from dataclasses import dataclass,field
from django.contrib.auth.models import AbstractUser
import os



# Create your models here.
class User (AbstractUser):
    email = models.EmailField (unique=True)
    full_name = models.CharField(max_length=255,blank=True)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return self.email



class Video(models.Model):
    
    STATUS_CHOICES = [
        ("EN ATTENTE",'en attente'),
        ("EN COURS DE TRAITEMENT",'en cours de traitement'),
        ('TERMINE','termine'),
        ('ECHOUE','echoue'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='videos')
    titre = models.CharField(max_length=255,blank=True)
    original = models.FileField(upload_to='videos/originals')
    traite = models.FileField(upload_to='videos/traite',blank=True,null=True)
    thumbnail =  models.ImageField(upload_to="videos/thumbnails/",blank=True,null=True)
    audio = models.FileField(upload_to="videos/audio",blank=True,null=True)
    status = models.CharField(max_length=22,choices=STATUS_CHOICES,default='EN ATTENTE')
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.titre or f"video {self.id}" # type: ignore

class ExportJob(models.Model):
    """modele de traque des exportations"""
    STATUS_CHOICES = [
        ("EN ATTENTE",'en attente'),
        ("EN COURS DE TRAITEMENT",'en cours de traitement'),
        ('TERMINE','termine'),
        ('ECHOUE','echoue'),
    ]

    video       = models.ForeignKey("Video", on_delete=models.CASCADE, related_name="exports")
    task_id     = models.CharField(max_length=255, unique=True, db_index=True)
    fmt         = models.CharField(max_length=10)
    qualite    = models.CharField(max_length=20)
    status      = models.CharField(max_length=22, choices=STATUS_CHOICES, default="EN ATTENTE")
    output_path = models.TextField(blank=True, null=True)
    mes_erreur   = models.TextField(blank=True, null=True)
    date  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ExportJob({self.task_id}) — {self.status}"


class ClipExportJob(models.Model):
    """modele de traque des exportations de clips"""
    STATUS_CHOICES = [
        ("EN ATTENTE",'en attente'),
        ("EN COURS DE TRAITEMENT",'en cours de traitement'),
        ('TERMINE','termine'),
        ('ECHOUE','echoue'),
    ]

    clip        = models.ForeignKey("VideoClip", on_delete=models.CASCADE, related_name="exports")
    task_id     = models.CharField(max_length=255, unique=True, db_index=True)
    fmt         = models.CharField(max_length=10)
    qualite     = models.CharField(max_length=20)
    status      = models.CharField(max_length=22, choices=STATUS_CHOICES, default="EN ATTENTE")
    output_path = models.TextField(blank=True, null=True)
    mes_erreur  = models.TextField(blank=True, null=True)
    date        = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ClipExportJob({self.task_id}) — {self.status}"
    

class Watermark(models.Model):
    image = models.ImageField(upload_to="watermarks/")

    def __str__(self) -> str:
        return f"Watermark({self.id})" # type: ignore

class RealTimeClippingJob(models.Model):
    """modele de traque de la creation des reels"""
    STATUS_CHOICES = [
        ("EN ATTENTE","en attente"),
        ("SON EXTRAIT","son extrait"),
        ("CLIPEE",'clipee'),
        ("PORTRAIT",'portrait'),
        ("SON AMELIORE","son ameliore"),
        ('THUMBNAIL',"thumbnail"),
        ('COMPRESSEE',"compressee"),
        ("TERMINE","termine"),
        ('ECHOUE',"echoue")
    ]
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    status      = models.CharField(max_length=22, choices=STATUS_CHOICES, default="EN ATTENTE")
    mes_erreur   = models.TextField(blank=True, null=True)
    date  = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"RealTimeClippingJob({self.id} - {self.status})"

def clip_upload_path(instance,filename):
    return os.path.join("videos","clips",str(instance.job.video.id),filename)

class VideoClip(models.Model):
    STATUS_CHOICES = [
        ("EN ATTENTE",'en attente'),
        ("EN COURS DE TRAITEMENT",'en cours de traitement'),
        ('TERMINE','termine'),
        ('ECHOUE','echoue'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='clips')
    job = models.ForeignKey(RealTimeClippingJob,on_delete=models.CASCADE,related_name="clips")
    clip = models.FileField(upload_to=clip_upload_path)
    status  = models.CharField(max_length=22, choices=STATUS_CHOICES, default="EN ATTENTE")
    debut = models.TimeField()
    fin = models.TimeField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Clip {self.id} du travail de conversion en reel {self.job.id} de ({self.debut} a {self.fin})"
    



@dataclass
class TextStyle: #style de texte pour les sous titres
    font:str = "Montserrat-bold"
    fontsize: int = 40
    fontcolor: str="#ffffff"
    align:str="center"
    box:bool= True
    boxcolor:str="#000000@0.80"
    boxborderw:int = 7
    bordercolor: str = "black"
    borderw:int = 8
    line_spacing: int = 8
        
@dataclass
class TextClip: #gestions des sous titres texte par texte
    text:str 
    start:float | None 
    end:float | None
    x: str | int ="w-text_w/2"  #au centre ou a preciser
    y: str | int ="h-100"
    style: TextStyle = field(default_factory=TextStyle)

    def to_ffmpeg_filter (self)  : #retourne le filtre ffmpeg correspondant au style et au texte
        texte_formatte = (self.text.replace("'","\\'")
                          .replace(":","\\:")
                          .replace(",","\\,")
                          .replace("\n","\\n")) #pour eviter les conflits avec la syntaxe de ffmpeg
        filtre = (
            f"drawtext=fontfile='{self.style.font}':"
            f"text='{texte_formatte}:"
            f"fontsize={self.style.fontsize}:"
            f"fontcolor={self.style.fontcolor}:"
            f"bordercolor={self.style.bordercolor}:"
            f"borderw={self.style.borderw}:"
            f"x={self.x}:"
            f"y={self.y}:"
            f"line_spacing={self.style.line_spacing}:"
        )
        if self.style.box:
            filtre += f"box=1:boxcolor={self.style.boxcolor}:boxborderw={self.style.boxborderw}"
        if self.start and self.end : 
            filtre +=  f"enable='between(t,{self.start},{self.end})'"
        return filtre

