from celery import shared_task
import os
import shutil
import subprocess
from django.conf import settings
from .models import ExportJob, Video,Watermark,RealTimeClippingJob,VideoClip
from .services.ffmpeg import resize_video, trim_video,rotate_video,crop_video,\
add_watermark,generate_thumbnail,text_overlay,extract_audio,\
enhance_audio,compress_video,portrait_blurr_background,portrait_classic,portrait_crop_center
import uuid

@shared_task
def video_processing(video_id, action, parameters):
    '''tache celery: envoyer la video ,l'action et les parametres a ffmpeg pour traitment'''
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'EN COURS DE TRAITEMENT'
        video.save()
        
        input_path = video.original.path
        output_filename = f"processed_{video_id}_{action}_{uuid.uuid4().hex}.mp4" #uuid4 permet de generer different nom pour plusieurs traitement d'une meme video
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'traite', output_filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        result = None

        if action == "trim":
            start = parameters.get('start', '00:00:00')
            end = parameters.get('end', '00:01:00')
            result = trim_video(input_path, output_path, start, end)
        
        elif action == "resize":
            width = parameters.get('width', 640)
            height = parameters.get('height', 480)
            result = resize_video(input_path, output_path, width, height)
        
        elif action == "rotate":
            degrees = parameters.get('degrees',90)
            result = rotate_video(input_path,output_path,degrees)

        elif action == "crop":
            width = parameters.get('width',100)
            height = parameters.get('height',100)
            x = parameters.get('x',0)
            y = parameters.get('y',0)
            result = crop_video(input_path,output_path,width,height,x,y)
        
        elif action == "watermark":
            x = parameters.get('x',10)
            y = parameters.get('y',10)
            scale = parameters.get('scale',15)
            watermark_id = parameters.get('id')
            watermark = Watermark.objects.get(id=watermark_id)
            watermark_path = watermark.image.path
            result = add_watermark(input_path,watermark_path,output_path,scale,x,y)

        elif action == "thumbnail":
            timestamp = parameters.get('timestamp','00:00:01')
            output_filename = f"thumbnail_{video_id}_{uuid.uuid4().hex}.jpg"
            output_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'thumbnails', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result = generate_thumbnail(input_path,output_path,timestamp)

        elif action == "text_overlay":
            text = parameters.get('text','')
            x = parameters.get('x','(w-text_w)/2') 
            y = parameters.get ('y','h-100')
            fontsize = parameters.get('fontsize',40)
            style = parameters.get('style',1)
            result = text_overlay(input_path,output_path,text,x,y,fontsize,style)



        

   
       #si le resultat est 0 ou le fichier d'output existe le traitement est reussi
        if (result is not None and result.returncode == 0) or os.path.exists(output_path):
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            video.traite = relative_path
            video.status = 'TERMINE'
            video.save()
            return f"Traitemtent de la video {video_id} avec action {action} reussi"
        else:
            video.status = 'ECHOUE'
            video.save()
            stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
            return f"Traitement de la video {video_id} echoue: {stderr}"
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors du traitement de la video {video_id}: {str(e)}"



@shared_task
def sound_extracting(job_id):
    """tache celery: extraction du son pour generation des sous titres"""
    try:
        job =  RealTimeClippingJob.objects.get(id=job_id)
        video_id = job.video.id
        video = Video.objects.get(id=video_id)  
        video.status = 'EN COURS DE TRAITEMENT'
        video.save()      
        input_path = video.original.path
        output_filename = f"audio_{video_id}_{uuid.uuid4().hex}.mp3" 
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'audio', output_filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        result = extract_audio(input_path,output_path)

        if (result is not None and result.returncode == 0) or os.path.exists(output_path):
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            video.audio = relative_path
            job.status = "SON EXTRAIT"
            video.status = "TERMINE"
            video.save()
            job.save()
            return job_id
        else:
            video.status = 'ECHOUE'
            video.save()
            stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
            return f"extraction du son de la video {video_id} echoue: {stderr}"
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors de l'extraction du son de la video {video_id}: {str(e)}"



@shared_task
def video_trimming (job_id,params):
    """tache celery: couper la video en clip"""
    try:
        job =  RealTimeClippingJob.objects.get(id=job_id)
        video_id = job.video.id
        video = Video.objects.get(id=video_id)
        video.status = 'EN COURS DE TRAITEMENT'
        video.save() 
    
        input_path = video.original.path 
        clips_timeline = params.get('clips',[])
        #creation du fichier et du nom de chaque clip
        for i,(start,end) in enumerate(clips_timeline):
            clip = VideoClip.objects.create(
                job = job,
                debut = clips_timeline[i][start],
                fin = clips_timeline[i][end]
            )
            output_filename = f"clip{i+1}_of_video{video_id}_{uuid.uuid4().hex}.mp4"
            output_path =  os.path.join(settings.MEDIA_ROOT, 'videos', 'clips',f'{video_id}', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result = trim_video (input_path,output_path,clip.debut,clip.fin)

            if (result is not None and result.returncode == 0) or os.path.exists(output_path):
                relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
                clip.clip = relative_path
                clip.save()
                video.status = "TERMINE"
                video.save()
            else:
                video.status = 'ECHOUE'
                video.save()
                stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
                return f"coupe de la video {video_id} echoue: {stderr}"
        job.status = "CLIPEE"
        job.save()
        return job_id
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors de la coupe de la video {video_id}: {str(e)}"


@shared_task
def converting_to_portrait (job_id,params):
    try:
        job =  RealTimeClippingJob.objects.get(id=job_id)
        video_id = job.video.id
        video = Video.objects.get(id=video_id)
        all_clips = job.clips.all()
        mode = params.get('mode')
        for i,clip in enumerate(all_clips):
            clip.status = "EN COURS DE TRAITEMENT"
            clip.save()
            input_path = clip.clip.path
            output_filename = f"clip_portrait{i+1}_of_video{video_id}_{uuid.uuid4().hex}.mp4"
            output_path =  os.path.join(settings.MEDIA_ROOT, 'videos', 'clips',f'{video_id}', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if mode == 'crop':
                result = portrait_crop_center(input_path,output_path)
            elif mode == "blur":
                result = portrait_blurr_background(input_path,output_path)
            else:
                result = portrait_classic(input_path,output_path)

            if (result is not None and result.returncode == 0) or os.path.exists(output_path):
                #suppression du clip avant la conversion en portrait
                shutil.move(output_path,input_path)
                #relative_path = os.path.relpath(input_path, settings.MEDIA_ROOT)
                clip.clip = input_path
                clip.status = "TERMINE"
                clip.save()
            else:
                clip.status = 'ECHOUE'
                clip.save()
                stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
                return f"conversion en portrait de la video {video_id} echoue: {stderr}"
        job.status = "PORTRAIT"
        job.save()
        return job_id
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors de la conversion en portrait de la video {video_id}: {str(e)}"


@shared_task
def enhancing_audio(job_id):
    try:
        job =  RealTimeClippingJob.objects.get(id=job_id)
        video_id = job.video.id
        video = Video.objects.get(id=video_id)
        all_clips = job.clips.all()
        for i,clip in enumerate(all_clips):
            clip.status = "EN COURS DE TRAITEMENT"
            clip.save()
            input_path = clip.clip.path
            output_filename = f"clip_portrait{i+1}_of_video{video_id}_{uuid.uuid4().hex}.mp4"
            output_path =  os.path.join(settings.MEDIA_ROOT, 'videos', 'clips',f'{video_id}', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            result = enhance_audio(input_path,output_path)

            if (result is not None and result.returncode == 0) or os.path.exists(output_path):
                #suppression du clip avant la conversion en portrait
                shutil.move(output_path,input_path)
                #relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
                clip.clip = input_path
                clip.status = "TERMINE"
                clip.save()
            else:
                clip.status = 'ECHOUE'
                clip.save()
                stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
                return f"amelioration du son  de la video {video_id} echoue: {stderr}"
        job.status = "SON AMELIORE"
        job.save()
        return job_id
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors de l'amelioration du son  de la video {video_id}: {str(e)}"

@shared_task
def video_compressing(job_id):
    try:
        job =  RealTimeClippingJob.objects.get(id=job_id)
        video_id = job.video.id
        video = Video.objects.get(id=video_id)
        all_clips = job.clips.all()
        for i,clip in enumerate(all_clips):
            clip.status = "EN COURS DE TRAITEMENT"
            clip.save()
            input_path = clip.clip.path
            output_filename = f"clipf_portrait{i+1}_of_video{video_id}_{uuid.uuid4().hex}.mp4"
            output_path =  os.path.join(settings.MEDIA_ROOT, 'videos', 'clips',f'{video_id}', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            result = compress_video(input_path,output_path)

            if (result is not None and result.returncode == 0) or os.path.exists(output_path):
                #suppression du clip avant la conversion en portrait
                shutil.move(output_path,input_path)
                #relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
                clip.clip = input_path
                clip.status = "TERMINE"
                clip.save()
            else:
                clip.status = 'ECHOUE'
                clip.save()
                stderr = getattr(result, 'stderr', None) if result is not None else 'no result'
                return f"compression   de la video {video_id} echoue: {stderr}"
        job.status = "COMPRESSEE"
        job.save()
        return job_id
    
    except Video.DoesNotExist:
         return f"Video {video_id} introuvable"
    except Exception as e:
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'ECHOUE'
            video.save()
        except:
            pass
        return f"Erreur lors de la compression  de la video {video_id}: {str(e)}"



@shared_task(bind=True)
def video_exporting(self, video_id, fmt, quality):
    '''tache celery :exporter une video traiter avec la qualite et le format choisi '''
    
    job = None
    try:
        
        job = ExportJob.objects.get(task_id=self.request.id)
        job.status = "EN COURS DE TRAITEMENT"
        job.save(update_fields=["status"])

        
        video = Video.objects.get(id=video_id)
        input_path = video.traite.path

      
        quality_bitrates = {
            "low":    "500k",
            "medium": "1500k",
            "high":   "3000k",
        }
        ext_map = {
            "mp4":  "mp4",
            "webm": "webm",
            "avi":  "avi",
            "mov":  "mov",
        }
        bitrate = quality_bitrates.get(quality, "1500k")
        ext     = ext_map.get(fmt, "mp4")

        output_filename = f"export_{video_id}_{quality}.{ext}"
        output_path     = os.path.join(
            settings.MEDIA_ROOT, "videos", "exports", output_filename
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

      
        command = ["ffmpeg", "-i", input_path, "-b:v", bitrate, "-y"]

        if fmt == "mp4":
            command.extend(["-c:v", "libx264", "-c:a", "aac", "-preset", "medium"])
        elif fmt == "webm":
            command.extend(["-c:v", "libvpx-vp9", "-c:a", "libopus"])
        elif fmt == "avi":
            command.extend(["-c:v", "mpeg4", "-c:a", "libmp3lame"])
        elif fmt == "mov":
            command.extend(["-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart"])

        command.append(output_path)

      
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0 or not os.path.exists(output_path):
            raise RuntimeError(f"FFmpeg echoue: {result.stderr}")

        
        job.status  = "TERMINE"
        job.output_path = output_path
        job.save(update_fields=["status", "output_path"])

        return {"status": "TERMINE", "output_path": output_path}

    except Exception as exc:
        if job:
            job.status  = "ECHOUE"
            job.mes_erreur= str(exc)
            job.save(update_fields=["status", "mes_erreur"])

        # Reesayer 3 fois maximum
        raise self.retry(exc=exc, countdown=2 ** self.request.retries, max_retries=3)