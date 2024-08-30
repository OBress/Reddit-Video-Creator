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

subreddits = []

accounts = {
}

load_dotenv()
gpt = gpt.GPT(env)
scrap = scraper.Scraper(env,subreddits)

# Change for how many videos you want generated for each account
for profile_name,profile_pic in accounts.items():
    for folder in os.listdir("tempFiles"):
        if os.path.isdir("tempFiles/" + folder):

            for i,f in enumerate(os.listdir("tempFiles/" + folder)):
                # print(f"tempFiles/{folder}/{f[:-4]}.wav")
                # AUDIO
                if f.endswith('.txt') and not os.path.exists(f"tempFiles/{folder}/{f[:-4]}.wav") and f[0] != '0':
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
                    
                else:
                    i -= 1
                
                    
            # Subtitles
            
            curDir = os.path.join("tempFiles/" + folder)
            print(f"\n\nCreating Subtitles for {folder}...")
            if env['SUBTITLES'].upper() == 'TRUE' and not os.path.exists(f"tempFiles/{folder}/{f[:-4]}.srt") :
                subtitlesPath = curDir
                print(subtitlesPath)
                aligner = MFA.ForcedAligner()
                aligner.align(subtitlesPath, subtitlesPath)
            else:
                subtitlesPath = None

            print("Done Subtitles")    