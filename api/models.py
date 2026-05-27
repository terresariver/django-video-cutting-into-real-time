from django.db import models

# Create your models here.
class Video(models.Model):
    
    STATUS_CHOICES = [
        ("EN ATTENTE",'en attente'),
        ("EN COURS DE TRAITEMENT",'en cours de traitement'),
        ('TERMINE','termine'),
        ('ECHOUE','echoue'),
    ]
    titre = models.CharField(max_length=255,blank=True)
    original = models.FileField(upload_to='videos/originals')
    traite = models.FileField(upload_to='videos/traite',blank=True,null=True)
    thumbnail =  models.ImageField(upload_to="videos/thumbnails/",blank=True,null=True)
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
    

class Watermark(models.Model):
    image = models.ImageField(upload_to="watermarks/")

    def __str__(self) -> str:
        return f"Watermark({self.id})" # type: ignore