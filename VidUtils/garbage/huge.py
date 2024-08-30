import subprocess

input_file = "media/background/runway/1.mp4"
sqaureVid = "good test.mp4"
properAspect = "aspect.mp4"
bigProper = "bigAspect.mp4"
final = "final.mp4"

# Crop the video to the center square
command = [
    'ffmpeg',
    "-hwaccel", "cuda",  
    '-i', input_file,
    '-vf', f'crop=768:768:exact=1',
    '-c:a', 'copy',
    sqaureVid
]
subprocess.run(command)

# Crop the sqaure video to 9x19
crop_width = 432  # 768 * 9/16
crop_height = 768
command = [
    "ffmpeg",
    "-hwaccel", "cuda",               # Use GPU for hardware acceleration
    "-i", sqaureVid,
    "-vf", f"crop={crop_width}:{crop_height}",
    "-c:v", "h264_nvenc",             # Use NVIDIA's hardware-accelerated H.264 encoder
    properAspect
]
subprocess.run(command)

# Scale the cropped 9/16 video to 768x1366
command = [
    'ffmpeg',
    '-i', properAspect,                        # Input file
    '-vf', 'scale=768:1366,boxblur=30:1', # Scaling filter with blur effect
    '-c:v', 'h264_nvenc',                   # Use NVIDIA hardware encoder
    '-preset', 'slow',                      # Encoding preset
    bigProper                               # Output file
]
subprocess.run(command)


# Overaly the sqaure video on the scaled 9/16 video
x_position = 0
y_position = (1366 - 768) // 2

command = [
    "ffmpeg",
    "-hwaccel", "cuda",  
    "-i", bigProper,
    "-i", sqaureVid,
    "-filter_complex", f"[0][1]overlay={0}:{y_position}",
    "-c:a", "copy",
    final
]


subprocess.run(command)
