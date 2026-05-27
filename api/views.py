import os
from django.shortcuts import render
from django.http import FileResponse
from .models import Video,ExportJob
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from .tasks import video_processing,video_exporting
from .serializers import VideoSerializer,WatermarkSerializer

#front end test
def test_process(request):
    return render(request,'test_process.html')

def test_export(request):
    return render(request,'test_export.html')


#upload video
@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser]) #verifier que l'on recoit un formData
def upload_video (request):
    '''Sauvegarde le fichier video recu et retourne les informations de la video sauvegarde(id,titre,date,...)'''
    serializer = VideoSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED) 
    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST) 

#upload watermark
@api_view(['POST'])
def upload_watermark(request):
    serializer = WatermarkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED) 
    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST) 



#traitement video
@api_view(['POST'])
def process_video (request):
    '''Traite la video d'id video_id en y effectuant l'action donne et retourne l'id de la tache'''
    try:
        video_id = request.data.get("video_id")
        action = request.data.get("action")
        parameters = request.data.get("params", {})
        
        if not video_id or not action:
            return Response({
                "erreur": "video id et action necessaires"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        video = Video.objects.get(id=video_id)
        
        task = video_processing.delay(video.id, action, parameters)
        return Response({
            'task_id': task.id,
            "message": "Traitement video demarre",
            "status": "En cours de traitement"
        }, status=status.HTTP_202_ACCEPTED)
    
    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video {video_id} introuvable"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#etat de traitement
@api_view(['GET'])
def process_status (request,video_id):
    '''renvoie l'etat de traitement de la video video_id'''
    try:
        if not video_id :
            return Response({
                "erreur": "video id necessaire"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        video = Video.objects.get(id=video_id)
        return Response({
            "status": video.status
        }, status=status.HTTP_202_ACCEPTED)
    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video {video_id} introuvable"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#export/download processed video
@api_view(["POST"])
def export_video(request):
    ''' Declenche un tache celery d'export et retourne  task_id '''

    try:
        video_id = request.data.get("video_id")
        fmt      = request.data.get("format",  "mp4")
        quality  = request.data.get("quality", "medium")

        if not video_id:
            return Response(
                {"erreur": "video_id necessaire"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video = Video.objects.get(id=video_id)

        if not video.traite:
            return Response(
                {"erreur": "Video traite indisponible"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if video.status != "TERMINE":
            return Response(
                {"erreurr": f"Le status de la video est {video.status}. Ne peut exporter que les videos terminees."},
                status=status.HTTP_400_BAD_REQUEST,
            )

     
        task = video_exporting.delay(video_id, fmt, quality)

        ExportJob.objects.create(
            video    = video,
            task_id  = task.id,
            fmt      = fmt,
            qualite  = quality,
            status   = "EN ATTENTE",
        )


        return Response(
            {
                "task_id": task.id,
                "status":  "EN ATTENTE",
                "message": "Export declanche. verifier /export/status/<task_id>/ .",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    except Video.DoesNotExist:
        return Response(
            {"error": f"Video {video_id} introuvable"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def export_status(request, task_id):
    '''Point de verification , retourne le status et  l'URL de telechargemt download URL when DONE.
    '''
    try:
        job = ExportJob.objects.get(task_id=task_id)
    except ExportJob.DoesNotExist:
        return Response({"erreur": "Tache non trouve"}, status=status.HTTP_404_NOT_FOUND)

    payload = {"task_id": task_id, "status": job.status}

    if job.status == "TERMINE":
        payload["download_url"] = f"/export/download/{task_id}/"
    elif job.status == "ECHOUE":
        payload["error"] = job.mes_erreur

    return Response(payload)


@api_view(["GET"])
def export_download(request, task_id):
    """
    Renvoie le fichier traite une fois que l'exportation est termine
    """
    try:
        job = ExportJob.objects.get(task_id=task_id, status="TERMINE")
    except ExportJob.DoesNotExist:
        return Response(
            {"erreur": "Exportation non trouve ou pas termine"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if not os.path.exists(job.output_path):
        return Response({"erreur": "Fichier non trouve"}, status=status.HTTP_404_NOT_FOUND)

    filename = os.path.basename(job.output_path)
    response  = FileResponse(open(job.output_path, "rb"), content_type="video/mp4")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response