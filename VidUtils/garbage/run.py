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

#  TAGS FOR TIKTOK
# #redditjudge #reddit #redditstories #storytime #story #minecraftparkour #drama 
# 'cheating_stories','weddingshaming','offmychest','TrueOffMyChest','AmItheAsshole'
subreddits = ['cheating_stories','offmychest','AmItheAsshole','TrueOffMyChest','AITAH','TrueOffMyChest','tifu','pettyrevenge','SupportforWaywards','relationship_advice','relationships','TwoHotTakes', 'familydrama','survivinginfidelity','entitledparents']

accounts = {
    # "Angel Of Reddit" : "angelofreddit",
    "Listen By Listening" : "listenbylistening"
}

load_dotenv()
gpt = gpt.GPT(env)
scrap = scraper.Scraper(env,subreddits)

# mode 0 - TTS      mode 1 - VIDEO
mode = 1

# Change for how many videos you want generated for each account
numVids = 1
for profile_name,profile_pic in accounts.items():
    for folder in os.listdir("tempFiles"):
        if os.path.isdir("tempFiles/" + folder):
            for i,f in enumerate(os.listdir("tempFiles/" + folder)):
                # print(f"tempFiles/{folder}/{f[:-4]}.wav")
                # AUDIO
                if f.endswith('.txt') and not os.path.exists(f"tempFiles/{folder}/{f[:-4]}.wav") and f[0] != '0' and mode == 0:
                    curDir = os.path.join("tempFiles/" + folder)
                    print(f"\n\n------------------------------------------------On Video {i+1} For {profile_name}------------------------------------------------")
                    # Scrap title and content
                    with open(os.path.join(curDir,f), 'r', encoding='utf8') as file:
                        post = file.read().split('\n\n\n\n')
                    
                    f = f[:-4]
                    postTitle = post[0]
                    postTitleAndText = post[0]+post[1]
                    
                    # socialPost.create_social_post(curDir, f'{f}.png', postTitle, profile_name, profile_pic)

                    # Get gender/voice and expand acronyms
                    gender = gpt.getGender(postTitleAndText)

                    # AWS TTS
                    tts = aws_tts.AWSTTS()
                    
                    
                    print("Creating Audio File")
                    audioFile = tts.createAudio(post[0]+'\n\n\n\n'+post[1], curDir, gender, f"{f}.wav")
                    audioFile = f"tempFiles/Video-1/{f}.wav"
                    print("Created audio file: " + audioFile)

                    # IF GOOGLE TTS
                    # if os.path.exists(f'tts-audio-files/{postTitle[0:20]}.mp3'):
                    #     os.remove(f'tts-audio-files/{postTitle[0:20]}.mp3')
                    # # AMAZON TTS
                    # elif os.path.exists(f'tts-audio-files/{postTitle[0:20]}'):
                    #     os.remove(f'tts-audio-files/{postTitle[0:20]}')

                    # os.remove('tts-audio-files\subtitles.ass')
                    # os.remove(subtitlesPath)
                    # os.remove("social_post.png")
                else:
                    i -= 1
                
                    
            # Subtitles
            
            curDir = os.path.join("tempFiles/" + folder)
            print("Creating Subtitles...")
            if env['SUBTITLES'].upper() == 'TRUE':
                subtitlesPath = curDir
                print(subtitlesPath)
                aligner = MFA.ForcedAligner()
                if mode == 0:
                    aligner.align(subtitlesPath, subtitlesPath)
            else:
                subtitlesPath = None

            print("Done Subtitles")    
            

            # for fading inbetween videos
            video = 0
            fade = (4,4)


            # VIDEO  
            for i,f in enumerate(os.listdir("tempFiles/" + folder)):
                if f.endswith('.txt') and not os.path.exists(f"output/{profile_name}/{folder}/temp/{f[:-4]}.mp4") and f[0] != '0' and mode == 1:
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

                    # IF GOOGLE TTS
                    # if os.path.exists(f'tts-audio-files/{postTitle[0:20]}.mp3'):
                    #     os.remove(f'tts-audio-files/{postTitle[0:20]}.mp3')
                    # # AMAZON TTS
                    # elif os.path.exists(f'tts-audio-files/{postTitle[0:20]}'):
                    #     os.remove(f'tts-audio-files/{postTitle[0:20]}')
                    if os.path.exists('subtitles.ass'):
                        os.remove('subtitles.ass')
                    # os.remove(subtitlesPath)
                    if mode == 1:
                        os.remove("social_post.png")
                else:
                    i -= 1
            if mode == 1:
                videos_location = f"output/{profile_name}/{folder}/temp"
                order_location = f"tempFiles/{folder}/0.txt"
                title_location = f"tempFiles/{folder}/"
                combine.concatenate_videos_in_folder(videos_location, f"{videos_location}/.final.mp4", order_location, title_location)