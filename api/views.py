import os
from django.shortcuts import render
from django.http import FileResponse
from .models import Video,ExportJob,ClipExportJob,RealTimeClippingJob,VideoClip,User
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from .tasks import video_processing,video_exporting,clip_exporting,sound_extracting,video_trimming,converting_to_portrait,enhancing_audio,video_compressing
from .serializers import VideoSerializer,WatermarkSerializer,RegisterSerializer,LoginSerializer,UserSerializer
from celery import chain
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken




#auth views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    '''Enregistre un nouvel utilisateur et retourne les tokens JWT'''
    try:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    '''Authentifie un utilisateur et retourne les tokens JWT'''
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)

            if user is None:
                return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    '''Deconnecte l\'utilisateur et blacklist le refresh token'''
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'refresh token necessaire'}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Deconnexion reussie'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_login(request):
    return render(request,'test_login.html')

def test_logout(request):
    return render(request,'test_logout.html')

def test_process(request):
    return render(request,'test_process.html')

def test_export(request):
    return render(request,'test_export.html')


#upload video
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser,FormParser])
def upload_video (request):
    '''Sauvegarde le fichier video recu et retourne les informations de la video sauvegarde(id,titre,date,...)'''
    try:
        serializer = VideoSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

#upload watermark
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_watermark(request):
    '''Sauvegarde le watermark recu'''
    try:
        serializer = WatermarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 



#traitement video
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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

        video = Video.objects.get(id=video_id, user=request.user)

        task = video_processing.delay(video.id, action, parameters)
        return Response({
            'task_id': task.id,
            "message": "Traitement video demarre",
            "status": "En cours de traitement"
        }, status=status.HTTP_202_ACCEPTED)

    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video introuvable ou acces refuse"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Creation des reels

def start_reel_process (job_id,params):
    chain(
        sound_extracting.s(job_id),
        video_trimming.s(params),
        converting_to_portrait.s(params),
        enhancing_audio.s(),
        video_compressing.s()
    ).apply_async()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_reels (request):
    try:
        video_id = request.data.get("video_id")
        parameters = request.data.get("params",{})

        if not video_id or not parameters:
            return Response({
                "erreur": "video id et temps de coupe necessaires"
            }, status=status.HTTP_400_BAD_REQUEST)

        video = Video.objects.get(id=video_id, user=request.user)
        job = RealTimeClippingJob.objects.create(
            video = video,
            status    = "EN ATTENTE",
        )
        start_reel_process(job.id,parameters)

        return Response({
            'job_id': job.id,
            "message": "Normalisation video demarre",
            "status": "En cours de normalisation"
        }, status=status.HTTP_202_ACCEPTED)

    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video introuvable ou acces refuse"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#etat de traitement
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def process_status (request,video_id):
    '''renvoie l'etat de traitement de la video video_id'''
    try:
        if not video_id :
            return Response({
                "erreur": "video id necessaire"
            }, status=status.HTTP_400_BAD_REQUEST)

        video = Video.objects.get(id=video_id, user=request.user)
        return Response({
            "status": video.status
        }, status=status.HTTP_202_ACCEPTED)
    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video introuvable ou acces refuse"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#export/download processed video
@api_view(["POST"])
@permission_classes([IsAuthenticated])
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

        video = Video.objects.get(id=video_id, user=request.user)

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
            {"error": f"Video introuvable ou acces refuse"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_status(request, task_id):
    '''Point de verification , retourne le status et  l'URL de telechargement download URL
    '''
    try:
        job = ExportJob.objects.get(task_id=task_id, video__user=request.user)
    except ExportJob.DoesNotExist:
        return Response({"erreur": "Tache non trouve"}, status=status.HTTP_404_NOT_FOUND)

    payload = {"task_id": task_id, "status": job.status}

    if job.status == "TERMINE":
        payload["download_url"] = f"/export/download/{task_id}/"
    elif job.status == "ECHOUE":
        payload["error"] = job.mes_erreur

    return Response(payload)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_download(request, task_id):
    """
    Renvoie le fichier traite une fois que l'exportation est termine
    """
    try:
        job = ExportJob.objects.get(task_id=task_id, video__user=request.user, status="TERMINE")
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


#export/download clip
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def export_clip(request):
    '''Declenche une ou plusieurs taches celery d'export de clips et retourne les task_ids'''

    try:
        clip_ids = request.data.get("clip_ids")
        if isinstance(clip_ids, int):
            clip_ids = [clip_ids]
        elif not isinstance(clip_ids, list):
            clip_ids = [clip_ids]

        fmt      = request.data.get("format",  "mp4")
        quality  = request.data.get("quality", "medium")

        if not clip_ids or len(clip_ids) == 0:
            return Response(
                {"erreur": "clip_ids necessaire"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exports = []
        errors = []

        for clip_id in clip_ids:
            try:
                clip = VideoClip.objects.get(id=clip_id, user=request.user)

                if clip.status != "TERMINE":
                    errors.append({
                        "clip_id": clip_id,
                        "erreur": f"Le status du clip est {clip.status}. Ne peut exporter que les clips termines."
                    })
                    continue

                task = clip_exporting.delay(clip_id, fmt, quality)

                export_job = ClipExportJob.objects.create(
                    clip     = clip,
                    task_id  = task.id,
                    fmt      = fmt,
                    qualite  = quality,
                    status   = "EN ATTENTE",
                )

                exports.append({
                    "clip_id": clip_id,
                    "task_id": task.id,
                    "status":  "EN ATTENTE",
                })

            except VideoClip.DoesNotExist:
                errors.append({
                    "clip_id": clip_id,
                    "erreur": "Clip introuvable ou acces refuse"
                })

        response_data = {"exports": exports}
        if errors:
            response_data["errors"] = errors

        return Response(
            response_data,
            status=status.HTTP_202_ACCEPTED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def clip_export_status(request, task_id):
    '''Point de verification ,retourne le status et l'url de telechargement download url
    '''
    try:
        job = ClipExportJob.objects.get(task_id=task_id, clip__user=request.user)
    except ClipExportJob.DoesNotExist:
        return Response({"erreur": "Tache non trouve"}, status=status.HTTP_404_NOT_FOUND)

    payload = {"task_id": task_id, "status": job.status}

    if job.status == "TERMINE":
        payload["download_url"] = f"/clip/export/download/{task_id}/"
    elif job.status == "ECHOUE":
        payload["error"] = job.mes_erreur

    return Response(payload)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def clip_export_download(request, task_id):
    """
    Renvoie le fichier clip une fois que l'exportation est terminee
    """
    try:
        job = ClipExportJob.objects.get(task_id=task_id, clip__user=request.user, status="TERMINE")
    except ClipExportJob.DoesNotExist:
        return Response(
            {"erreur": "Exportation non trouvee ou pas terminee"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if not os.path.exists(job.output_path):
        return Response({"erreur": "Fichier non trouve"}, status=status.HTTP_404_NOT_FOUND)

    filename = os.path.basename(job.output_path)
    response  = FileResponse(open(job.output_path, "rb"), content_type="video/mp4")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


#suppression
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_video (request):
    '''supprime la video et tout ce qui y est lie'''
    try:
        video_id = request.data.get("video_id")
        if not video_id :
            return Response({
                "erreur": "video id et action necessaires"
            }, status=status.HTTP_400_BAD_REQUEST)

        video = Video.objects.get(id=video_id, user=request.user)
        os.remove(video.original.path)
        os.remove(video.traite.path)
        os.remove(video.audio.path)
        os.remove(video.thumbnail.path)
        video.delete()

        
        return Response({
            "message": "suppression reussie",
        }, status=status.HTTP_202_ACCEPTED)

    except Video.DoesNotExist:
        return Response({
            "erreur": f"Video introuvable ou acces refuse"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)