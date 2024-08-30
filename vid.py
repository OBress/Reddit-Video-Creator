import os
import re
from os import environ as env
from pathlib import Path
from dotenv import load_dotenv
from VidUtils import scraper
from VidUtils import aws_tts
from VidUtils import videoGen
from VidUtils import MFA
from VidUtils import gpt
from VidUtils import socialPost
from VidUtils import combine

accounts = {
}

load_dotenv()
gpt = gpt.GPT(env)

for profile_name,profile_pic in accounts.items():
    for folder in os.listdir("tempFiles"):
        if os.path.isdir("tempFiles/" + folder):
            # for fading inbetween videos
            video = 0
            fade = (4,4)

            subtitlesPath = os.path.join("tempFiles/" + folder)
            # VIDEO  
            for i,f in enumerate(os.listdir("tempFiles/" + folder)):
                if f.endswith('.txt') and not os.path.exists(f"output/{profile_name}/{folder}/temp/{f[:-4]}.mp4") and f[0] != '0':
                    curDir = os.path.join("tempFiles/" + folder)
                    print(f"\n\n------------------------------------------------On Video {i+1} For {profile_name}------------------------------------------------")
                    # Scrap title and content
                    with open(os.path.join(curDir,f), 'r', encoding='utf8') as file:
                        post = file.read().split('\n\n\n\n')
                    
                    f = f[:-4]
                    postTitle = post[0]
                    postTitleAndText = post[0]+post[1]

                    audioFile = f"tempFiles/{folder}/{f}.wav"
                    videoCreator = videoGen.VideoGenerator(env)
                    background_directory = 'media/background/videos'
                    audio_directory = 'media/background/audios'
                    name = f

                    outputPath = os.path.join(f'output/{profile_name}/{folder}/temp', f'{name}.mp4')
                    bgVideoFileName = env['BG_VIDEO_FILENAME']
                    # Create folder for channel videos
                    if not os.path.exists(f'output/{profile_name}'):
                        os.makedirs(f'output/{profile_name}')
                    if not os.path.exists(f'output/{profile_name}/{folder}'):
                        os.makedirs(f'output/{profile_name}/{folder}')
                    if not os.path.exists(f'output/{profile_name}/{folder}/temp'):
                        os.makedirs(f'output/{profile_name}/{folder}/temp')
                    
                    # calc fade for videos
                    video += 1
                    if video == 1:
                        fade = (4,4)
                    else:
                        fade = (4,4)


                    videoFile = videoCreator.generateVideo(
                        bgVideoFileName, audioFile, outputPath, background_directory, audio_directory, subtitlesPath+f"/{f}.srt", postTitle, profile_name, profile_pic, fade)
                    if (videoFile != False):
                        print("Created output video file at: " + videoFile)
                    else:
                        print("Failed to create output video file")

                    if os.path.exists('subtitles.ass'):
                        os.remove('subtitles.ass')
                    
                    if os.path.exists("social_post.png"):
                        os.remove("social_post.png")
                else:
                    i -= 1

            folder_path = f"output/{profile_name}/{folder}/"
            order_location = f"tempFiles/{folder}/0.txt"
            title_location = f"tempFiles/{folder}/"
            if not os.path.exists(f"{folder_path}/.final.mp4"):
                combine.concatenate_videos_in_folder(folder_path, f"{folder_path}/.final.mp4", order_location, title_location)