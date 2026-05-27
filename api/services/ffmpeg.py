import subprocess
from tempfile import NamedTemporaryFile
import os


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
    filter_complex = (
        f"[1:v]scale=iw*{scale}/100:-1[wm];"
        f"[0:v][wm]overlay=x={x}:y={y}"
    )
    command = [  
        "ffmpeg",
        "-i", input_path,
        "-i", watermark_path,
        "-filter_complex",filter_complex,
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






















