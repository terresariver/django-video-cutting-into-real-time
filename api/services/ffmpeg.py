import subprocess
from django.conf import settings
from tempfile import NamedTemporaryFile
import os


def resize_video(input_path, output_path, width, height):
    """Resize video to specified width and height"""
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
    """Trim video from start to end time"""
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
    """Rotate the video by 90, 180, or 270 degrees"""
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
    """Crop video to a region. x, y = top-left corner of the crop."""
    command = [
        "ffmpeg", "-i", input_path,
        "-vf", f"crop={width}:{height}:{x}:{y}",
        "-c:a", "copy",
        output_path
    ]
    return subprocess.run(command, check=True)

def concatenate_videos(input_paths, output_path):
    """Join multiple videos into a single output file"""
    with NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as list_file:
        for path in input_paths:
            list_file.write(f"file '{path}'\n")
        list_file.flush()
        command = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file.name,
            "-c", "copy",
            "-y",
            output_path
        ]
        result = subprocess.run(command, check=True)
        os.remove(list_file.name)
        return result




# def generate_thumbnail(input_path, output_path, timestamp="00:00:01"):
#     """Grab a single frame as a thumbnail image."""
#     command = [
#         "ffmpeg", "-i", input_path,
#         "-ss", timestamp,
#         "-vframes", "1",
#         output_path
#     ]
#     return subprocess.run(command, check=True)




# def add_watermark(input_path, watermark_path, output_path, x="10", y="10"):
#     """Overlay an image watermark onto the video"""
#     command = [
#         "ffmpeg",
#         "-i", input_path,
#         "-i", watermark_path,
#         "-filter_complex", f"overlay={x}:{y}",
#         "-codec:a", "copy",
#         "-y",
#         output_path
#     ]
#     subprocess.run(command, check=True)











# --- Audio ---

# def extract_audio(input_path, output_path):
#     """Extract audio track from a video (e.g. output: audio.mp3)."""
#     command = [
#         "ffmpeg", "-i", input_path,
#         "-vn", "-acodec", "copy",
#         output_path
#     ]
#     subprocess.run(command, check=True)

# def mute_video(input_path, output_path):
#     """Remove audio from a video entirely."""
#     command = [
#         "ffmpeg", "-i", input_path,
#         "-an", "-c:v", "copy",
#         output_path
#     ]
#     subprocess.run(command, check=True)

# def merge_audio_video(video_path, audio_path, output_path):
#     """Replace a video's audio track with a separate audio file."""
#     command = [
#         "ffmpeg",
#         "-i", video_path,
#         "-i", audio_path,
#         "-c:v", "copy",
#         "-c:a", "aac",
#         "-map", "0:v:0",
#         "-map", "1:a:0",
#         "-shortest",
#         output_path
#     ]
#     subprocess.run(command, check=True)

# def adjust_volume(input_path, output_path, volume: float):
#     """
#     Adjust audio volume.
#     volume: 0.5 = half, 1.0 = original, 2.0 = double
#     """
#     command = [
#         "ffmpeg", "-i", input_path,
#         "-af", f"volume={volume}",
#         "-c:v", "copy",
#         output_path
#     ]
#     subprocess.run(command, check=True)


# --- Video Transformations ---

# def change_speed(input_path, output_path, speed: float):
#     """
#     Speed up or slow down a video.
#     speed: 0.5 = half speed, 2.0 = double speed
#     """
#     video_filter = f"setpts={1/speed}*PTS"
#     audio_filter = f"atempo={speed}"

#     # atempo only supports 0.5–2.0; chain filters for extreme values
#     if speed > 2.0:
#         audio_filter = "atempo=2.0,atempo=2.0"
#     elif speed < 0.5:
#         audio_filter = "atempo=0.5,atempo=0.5"

#     command = [
#         "ffmpeg", "-i", input_path,
#         "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
#         "-map", "[v]", "-map", "[a]",
#         output_path
#     ]
#     subprocess.run(command, check=True)







# # --- Conversion & Export ---
# def extract_frames(input_path, output_dir, fps=1):
#     """
#     Extract frames as images.
#     fps: frames per second to extract (1 = one frame per second)
#     Output files: frame_0001.png, frame_0002.png, ...
#     """
#     os.makedirs(output_dir, exist_ok=True)
#     command = [
#         "ffmpeg", "-i", input_path,
#         "-vf", f"fps={fps}",
#         os.path.join(output_dir, "frame_%04d.png")
#     ]
#     subprocess.run(command, check=True)


# def get_video_info(input_path) -> dict:
#     """Return basic video metadata using ffprobe."""
#     import json
#     command = [
#         "ffprobe", "-v", "quiet",
#         "-print_format", "json",
#         "-show_streams", "-show_format",
#         input_path
#     ]
#     result = subprocess.run(command, capture_output=True, text=True, check=True)
#     return json.loads(result.stdout)


# def change_audio_volume(input_path, output_path, volume=1.0):
#     """Change the audio volume of the video"""
#     command = [
#         "ffmpeg",
#         "-i", input_path,
#         "-filter:a", f"volume={volume}",
#         "-c:v", "copy",
#         "-y",
#         output_path
#     ]
#     subprocess.run(command, check=True)


# def extract_audio(input_path, output_path, audio_codec="aac"):
#     """Extract audio track from a video file"""
#     command = [
#         "ffmpeg",
#         "-i", input_path,
#         "-vn",
#         "-acodec", audio_codec,
#         "-y",
#         output_path
#     ]
#     subprocess.run(command, check=True)

