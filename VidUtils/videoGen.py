import ffmpeg
import math
import os
import random
import srt
import subprocess
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

ANIMS = True
PFPDIM = int(72)


class VideoGenerator:
    def __init__(self, env):
        self.env = env

    def generateVideo(self, backgroundVideoFileName, ttsAudioPath, outputVideoPath, background_directory, audio_directory, subtitlesPath, title, profile_name, profile_pic, fade):
        backgroundVideoPath = self.getBackgroundVideoPath(
            backgroundVideoFileName, background_directory)

        if not os.path.isfile(backgroundVideoPath):
            print(f"Video file not found: {backgroundVideoPath}")
            return False

        if not os.path.isfile(ttsAudioPath):
            print(f"Audio file not found: {ttsAudioPath}")
            return False

        audioDuration = self.getAudioDuration(ttsAudioPath)
        # Original Video
        videoProbe = ffmpeg.probe(backgroundVideoPath)
        videoStream = self.getVideoStream(videoProbe)
        videoDuration = float(videoStream['duration'])
        startTime = self.getStartTime(audioDuration, videoDuration)
        newVidPath = backgroundVideoPath[:-4]+'_temp.mp4'
        background_audio = self.getRandomFile(audio_directory)
        self.makeCopy(backgroundVideoPath, newVidPath, startTime)
        
        startTime = 0

        # Calculate new dimensions only when necessary
        newWidth, newHeight = videoStream['width'], videoStream['height']

        video, background_audio_delay = self.processVideo(
            newVidPath, videoDuration, audioDuration, startTime, newWidth, newHeight, subtitlesPath, title, profile_name, profile_pic, fade)


        audio = ffmpeg.input(ttsAudioPath)

        self.mergeAudioVideo(video, audio, background_audio, outputVideoPath, background_audio_delay)

        os.remove(newVidPath)
        
        return outputVideoPath

    def makeCopy(self, input_path, output_path, start_time):
        command = [
        'ffmpeg',
        '-ss', f"{start_time:.3f}",     # Start time
        '-i', input_path,      # Input file
        '-c', 'copy',     # Video codec
        output_path            # Output file
        ]

        subprocess.run(command, check=True)
        return output_path

    def getBackgroundVideoPath(self, backgroundVideoFileName, background_directory):
        if backgroundVideoFileName.upper() == 'RANDOM':
            return self.getRandomFile(background_directory)
        else:
            return os.path.join(background_directory, self.env['BG_VIDEO_FILENAME'])

    def getAudioDuration(self, ttsAudioPath):
        probe = ffmpeg.probe(ttsAudioPath)
        return float(probe['streams'][0]['duration'])+1

    def getVideoStream(self, videoProbe):
        return next((stream for stream in videoProbe['streams'] if stream['codec_type'] == 'video'), None)

    def getStartTime(self, audioDuration, videoDuration):
        randomizeStart = self.env['RANDOM_START_TIME'].upper() == 'TRUE'
        if videoDuration > audioDuration and randomizeStart:
            return random.uniform(1, videoDuration - audioDuration - 1)
        else:
            return 0

    def getNewDimensions(self, videoStream):
        width = int(videoStream['width'])
        height = int(videoStream['height'])

        if width / height > 9 / 16:  # wider than 9:16, crop sides
            return int(height * (9 / 16)), height
        else:  # narrower than 9:16, crop top and bottom
            return width, int(width * (16 / 9))

    def processVideo(self, backgroundVideoPath, videoDuration, audioDuration, startTime, newWidth, newHeight, subtitlesPath, title, profile_name, profile_pic, fade):
        video = ffmpeg.input(backgroundVideoPath)
        try:
            os.remove('subtitles.ass')
        except OSError as error:
            print("failed")
        if videoDuration < audioDuration:
            loopsNeeded = int(audioDuration // videoDuration) + 1
            videos = [video for _ in range(loopsNeeded)]
            video = ffmpeg.concat(*videos, v=1, a=0)

        # Trim the video to match the length of the audio and crop to the desired aspect ratio
        video = video.trim(start=startTime, end=startTime + audioDuration)
        video = ffmpeg.setpts(video, 'PTS-STARTPTS')

        # Crop the video to the desired aspect ratio if dimensions were calculated
        if newWidth is not None and newHeight is not None:
            video = ffmpeg.filter_(video, 'crop', newWidth, newHeight)

        self.create_social_post(
            title_text=title,
            profile_name=profile_name, 
            profile_pic=profile_pic,
            video_width=newHeight*(9/16),
            video_height=newHeight,
            likes_count="99+",
            comments_count="99+",
        )
        print("Done Intro")

        overlay_file = ffmpeg.input('social_post.png')
        title_words = title.split()
        last_word = title_words[-1].lower()

        if last_word.endswith(('.', '!', '?')):
            last_word = last_word[:-1]

        last_word_occurences = 0
        for word in title_words:
            if last_word in word.lower():
                last_word_occurences += 1

        file = open(subtitlesPath, 'r', encoding='utf8')
        subtitles = list(srt.parse(file.read()))
        start_video_time = subtitles[0].start / timedelta(milliseconds=1)
        end_title_time = 0
        occurence_count = 0
        for sub in subtitles:
            occurence_count += sub.content.lower().count(last_word)
            if occurence_count >= last_word_occurences:
                
                end_title_time = sub.end / timedelta(milliseconds=1)
                occurence_count = -math.inf
                break
        file.close()

        # Add subtitles if provided
        if subtitlesPath is not None and os.path.isfile(subtitlesPath):
            # Set style for the subtitles
            style = "FontName=Exo 2 Black,FontSize=20,PrimaryColour=&H00ffffff,OutlineColour=&H00000000,BackColour=&H80000000,Bold=1,Italic=0,Alignment=10,Outline=1.5,Encoding=0"
            if ANIMS:
                print("Generating Subtitle Animations")
                ffmpeg.input(subtitlesPath).output('subtitles.ass').run()
                subtitlesPath = 'subtitles.ass'
                file = open(subtitlesPath, 'r', encoding='utf8')
                unread_ass = file.read(-1)
                file.close()
                file = open(subtitlesPath, 'w+', encoding='utf8')
                read_ass = ""
                for sub in subtitles:
                    read_ass += unread_ass[0:unread_ass.index(sub.content)]
                    read_ass += r'{\t(0,100,\fscx105\fscy105)}'
                    read_ass += sub.content
                    unread_ass = unread_ass[unread_ass.index(sub.content)+len(sub.content):]
                file.write(read_ass)
                file.close()


            fade_out_start = audioDuration - fade[1]
            if fade[0]:
                video = video.filter('fade', type='in', start_time=0, duration=fade[0])
            if fade[1]:
                video = video.filter('fade', type='out', start_time=fade_out_start, duration=fade[1])
                
            print("Generating Video")
            split = (video.split())
            print("Split Good")

            video = ffmpeg.concat(
                ffmpeg.filter_(
                    [split[0].trim(start_frame=int(start_video_time * 0.06), end_frame=end_title_time * 0.06),
                     overlay_file], 'overlay',int(newWidth*0.326),int(newHeight*0.3)),
                ffmpeg.setpts(
                    ffmpeg.filter_(split[1].trim(start_frame=end_title_time * 0.06, end=audioDuration - 1), 'subtitles',
                                   subtitlesPath, force_style=style), 'PTS-STARTPTS')
            )

        return video, int(end_title_time * 0.06)

    def mergeAudioVideo(self, video, audio, background_audio, outputVideoPath, background_audio_delay):
        vcodec = self.env['VCODEC']
        numThreads = self.env['THREADS']

        backgroundMusic = ffmpeg.input(background_audio, stream_loop=-1).audio.filter('adelay', f'{background_audio_delay}|{background_audio_delay}').filter('volume', '0.30')
        mixedAudio = ffmpeg.filter([audio, backgroundMusic], 'amix', inputs=2, duration='first', dropout_transition=1)

        output = ffmpeg.output(video, mixedAudio, outputVideoPath, vcodec=vcodec, rc='vbr', cq=18, threads=numThreads)
        output = ffmpeg.overwrite_output(output)
        ffmpeg.run(output)

    def getRandomFile(self, directory):
        # Filter the list to include only .mp4 files
        mp4Files = [entry.path for entry in os.scandir(
            directory) if entry.is_file() and (entry.name.endswith('.mp4') or entry.name.endswith('.mp3'))]

        # Select a random .mp4 file
        randomMP4 = random.choice(mp4Files)
        print(f"Choose {randomMP4} For Background")
        
        return randomMP4

    def create_social_post(output_folder, title_text, profile_name, profile_pic, likes_count=99, comments_count=99, video_width=810, video_height=1440, font_size=50):

        # Create a new white background image
        PFPDIM = font_size * 3
        image_width = int(video_width * 1.1)
        image_height = int(video_height * 0.45)
        background = Image.new('RGBA', (image_width, image_height), '#00000000')
        draw = ImageDraw.Draw(background)

        # Define the font and size
        font_path = "media/fonts/Exo2-Black.ttf"  # Make sure this is the correct path
        try:
            title_font = ImageFont.truetype(font_path, font_size)
            interaction_font = ImageFont.truetype(font_path, int(font_size * 0.8))  # Smaller font for likes/comments
        except OSError as e:
            print(f"Error loading font: {e}")
            title_font = ImageFont.load_default()
            interaction_font = ImageFont.load_default()
            print("Default font loaded instead.")
        words = title_text.split()

        new_title_string = ""
        for word in words:
            (left, top, right, bottom) = draw.textbbox((0, 0), new_title_string + " "+ word, font=title_font)
            if right - left > image_width - font_size:
                new_title_string += "\n"
            new_title_string += " "+ word
        # Center the title text
        ascent, descent = title_font.getmetrics()
        (width, baseline), (offset_x, offset_y) = title_font.font.getsize(new_title_string)

        (left, top, right, bottom) = draw.textbbox((0, 0), new_title_string, font=title_font)
        title_text_width = right - left
        
        
        draw.rounded_rectangle([(0, 0), (image_width+8, bottom + PFPDIM + int(font_size*3.25))], int(PFPDIM/4), "#00000060")
        draw.rounded_rectangle([(0, 0), (image_width, bottom + PFPDIM + int(font_size*3.25))], int(PFPDIM/4), "#ffffffff")
        profile_clip = Image.new('RGBA', (PFPDIM, PFPDIM), '#00000000')
        profile_clip_draw = ImageDraw.Draw(profile_clip)
        profile_clip_draw.rounded_rectangle([(0, 0), (PFPDIM, PFPDIM)], int(PFPDIM/2), "#000000ff")

        profile_clip_mask = Image.new('RGBA', (PFPDIM, PFPDIM), '#000000ff')
        profile_clip_draw_mask = ImageDraw.Draw(profile_clip_mask)
        profile_clip_draw_mask.rounded_rectangle([(0, 0), (PFPDIM, PFPDIM)], int(PFPDIM/2), "#00000000")
        profilepic = Image.open(f"media/images/{profile_pic}.png").convert('RGBA')
        profilepic = profilepic.resize((int(PFPDIM), int(PFPDIM)))

        profilepic.paste(profile_clip, (0, 0), profile_clip_mask)
        background.paste(profilepic, (int(PFPDIM/4), int(PFPDIM/4)), profilepic)
        (_, name_top, right, name_bottom) = draw.textbbox((int(PFPDIM*1.65), int(PFPDIM*2/5)), profile_name, font=title_font)
        draw.text((int(PFPDIM*11/8), int(PFPDIM*2/5)), profile_name, font=title_font, fill='black')
        verified = Image.open("media/images/verified.png").convert('RGBA')
        verified = verified.resize((int(PFPDIM/3), int(PFPDIM/3)))
        background.paste(verified, (right-int(PFPDIM/4), int((name_top + name_bottom)/2) - int(PFPDIM/6)), verified)

        awards = ['1','bear','brain','business','covid','cry','dolphin','eagle','eyes','fire','fire','gold','golden','king','platinum','seal','silver','skele','stock','wave']
        for num in range(random.randint(8,11)):
            img = awards.pop(random.randint(0,len(awards)-1))
            award = Image.open(f"media/awards/{img}.png").convert('RGBA')
            award = award.resize((int(PFPDIM/4), int(PFPDIM/4)))
            background.paste(award, (int(PFPDIM* 1.25) +int(PFPDIM/8)+ int(PFPDIM/16)*num*5, PFPDIM - int(PFPDIM/8)), award)

        draw.multiline_text((20, PFPDIM + int(font_size)), new_title_string, font=title_font, fill='black')
        # Position the likes and comments below the title text
        interaction_text = f"❤️ {likes_count}   💬 {comments_count}"
        share_text = f"🌐  Share"
        (interaction_text_width, baseline), (offset_x, offset_y) = interaction_font.font.getsize(interaction_text)
        (share_text_width, share_text_baseline), (share_text_offset_x, share_text_offset_y) = interaction_font.font.getsize(interaction_text)
        with Pilmoji(background) as pilmoji:
            pilmoji.text((image_width-(share_text_width)-30, bottom + (ascent - offset_y + descent) + int(font_size*3.7)), share_text, font=interaction_font, fill='black')
            pilmoji.text((int(PFPDIM/4), bottom + (ascent - offset_y + descent) + int(font_size*3.7)), interaction_text, font=interaction_font, fill='black')
            
        # Save the resulting image
        background.save("social_post.png")
