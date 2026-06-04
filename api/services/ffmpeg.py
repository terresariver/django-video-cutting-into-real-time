import subprocess
from ..models import TextStyle,TextClip


def resize_video(input_path, output_path, width, height):
    """Redimensionner la video en fonction des parametres longueurs et largeurs"""
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale={width}x{height}",
        "-c:v", "libx264",
        "-c:a", "copy",
        "-y",
        output_path
    ]
    return subprocess.run(command,check=True)
        
    


def trim_video(input_path, output_path, start, end):
    """Couper la video en fonction de l'intervalle de temps mentionne"""
    command = [
        "ffmpeg",
        "-i", input_path,
        "-ss", start,
        "-to", end,
        "-c:v", "libx264",
        "-c:a", "copy",
        "-y",
        output_path
    ]
    return subprocess.run(command, check=True)

def rotate_video(input_path, output_path, degrees=90):
    """Faire tourner la video en fonction de l'angle donne"""
    degrees = degrees % 360
    if degrees == 90:
        rotate_filter = "transpose=1"
    elif degrees == 180:
        rotate_filter = "transpose=2,transpose=2"
    elif degrees == 270:
        rotate_filter = "transpose=2"
    else :
        rotate_filter = (f"rotate={degrees}*PI/180:"
                         f"ow=rotw({degrees}*PI/180):"
                         f"oh=roth({degrees}*PI/180)")
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", rotate_filter,
        "-c:a", "copy",
        "-y",
        output_path
    ]
    return subprocess.run(command, check=True)

def crop_video(input_path, output_path, width, height, x=0, y=0):
    """Recadrer la video en fonction de la longueur et de la largeur et a partir de la position x,y"""
    command = [
        "ffmpeg", "-i", input_path,
        "-vf", f"crop={width}:{height}:{x}:{y}",
        "-c:a", "copy",
        output_path
    ]
    return subprocess.run(command, check=True)

def add_watermark(input_path, watermark_path, output_path,scale=15, x="W-w-20", y="H-h-20"):
    """superposer une image a la video a partir de la position x,y"""
    filter = (
        f"[1:v]scale=iw*{scale}/100:-1[wm];"
        f"[0:v][wm]overlay=x={x}:y={y}"
    )
    command = [  
        "ffmpeg",
        "-i", input_path,
        "-i", watermark_path,
        "-filter_complex",filter,
        "-c:v", "libx264",
        "-preset","medium",
        "-crf","23",
        "-c:a", "copy",
        output_path
    ]
    return subprocess.run(command, check=True)


def generate_thumbnail(input_path, output_path, timestamp="00:00:01"):
    """Choisir une frame comme vignette"""
    command = [
        "ffmpeg", "-i", input_path,
        "-ss", timestamp,
        "-vframes", "1",
        output_path
    ]
    return subprocess.run(command, check=True)

def text_overlay (input_path,output_path,text="",x="w-text_w/2",y="h-100",fontsize=40,style=1):
    """superposer un texte a la video"""
    if style == 1 :
        Style = TextStyle()
    elif style == 2 :
        Style = TextStyle(fontcolor="#000000",boxcolor="#ffffff@0.80",bordercolor="white")
    elif style == 3 :
        Style = TextStyle(boxcolor="#ff0000@0.80")
    else :
        Style = TextStyle (boxcolor="#0000ff@0.80")
    filter= TextClip(text=text,start=None,end=None,x=x,y=y,style=Style).to_ffmpeg_filter()
    command = [
        "ffmpeg",
        "-i",input_path,
        "-vf",filter,
        "-c:a","copy",
        "-y",output_path
    ]
    return subprocess.run(command,check=True)

##Fonctions liees a la conversion au format reel

def extract_audio (input_path,output_path):
    """extrait l'audio d'une video en haute qualite (pour generation de sous titres)"""
    command = [
        "ffmpeg",
        "-i",input_path,
        "-vn","-acodec",
        "libmp3lame",
        "-q:a",
        "4",
        "-y",output_path
    ]
    return subprocess.run(command,check=True)

def portrait_classic(input_path,output_path):
    """convertir les videos en format portrait"""
    command = [
        "ffmpeg",
        "-i",input_path,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:a","copy",
        output_path
    ]
    return subprocess.run(command,check=True)

def portrait_crop_center (input_path,output_path):
    """convertir les videos en format portrait en coupant au centre"""
    command = [
        "ffmpeg",
        "-i",input_path,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:a","copy",
        output_path
    ]
    return subprocess.run(command,check=True)

def portrait_blurr_background (input_path,output_path):
    """convertir les videos en format portrait  et flouter l'arriere plan"""
    filter = (
        f"split[v1][v2];"
        f"[v1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=luma_radius=20:luma_power=1[bg];"
        f"[v2]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )
    command = [
        "ffmpeg",
        "-i",input_path,
        "-vf",filter,
        "-c:a","copy",
        output_path
    ]
    return subprocess.run(command,check=True)

def enhance_audio(input_path,output_path):
    """ameliorer la qualite du son"""
    command = [
        "ffmpeg",
        "-i",input_path,
        "-af","loudnorm",
        output_path
    ]
    return subprocess.run(command,check=True)

def compress_video (input_path,output_path):
    """compresser une video a une qualite moyenne"""
    command = [
        "ffmpeg",
        "-i",input_path,
        "-c:v","libx264",
        "-crf","23",
        "-preset","medium",
        output_path
    ]
    return subprocess.run(command,check=True)

























