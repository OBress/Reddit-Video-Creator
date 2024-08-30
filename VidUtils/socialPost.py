import math
import os
import random
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji




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

if __name__ == '__main__':
    create_social_post('output/', "Testing how this shit will work if I do a realisitc title, like this.", "A Youtube Channel", "ayoutubechannel")