# author: GiorDior aka Giorgio
# date: 12.06.2023
# topic: TikTok-Voice-TTS
# version: 1.0
# credits: https://github.com/oscie57/tiktok-voice

import threading, requests, base64
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play

VOICES = [
    # DISNEY VOICES
    'en_us_ghostface',            # Ghost Face
    'en_us_chewbacca',            # Chewbacca
    'en_us_c3po',                 # C3PO
    'en_us_stitch',               # Stitch
    'en_us_stormtrooper',         # Stormtrooper
    'en_us_rocket',               # Rocket

    # ENGLISH VOICES
    'en_au_001',                  # English AU - Female
    'en_au_002',                  # English AU - Male
    'en_uk_001',                  # English UK - Male 1
    'en_uk_003',                  # English UK - Male 2
    'en_us_001',                  # English US - Female (Int. 1)
    'en_us_002',                  # English US - Female (Int. 2)
    'en_us_006',                  # English US - Male 1
    'en_us_007',                  # English US - Male 2
    'en_us_009',                  # English US - Male 3
    'en_us_010',                  # English US - Male 4

    # EUROPE VOICES
    'fr_001',                     # French - Male 1
    'fr_002',                     # French - Male 2
    'de_001',                     # German - Female
    'de_002',                     # German - Male
    'es_002',                     # Spanish - Male

    # AMERICA VOICES
    'es_mx_002',                  # Spanish MX - Male
    'br_001',                     # Portuguese BR - Female 1
    'br_003',                     # Portuguese BR - Female 2
    'br_004',                     # Portuguese BR - Female 3
    'br_005',                     # Portuguese BR - Male

    # ASIA VOICES
    'id_001',                     # Indonesian - Female
    'jp_001',                     # Japanese - Female 1
    'jp_003',                     # Japanese - Female 2
    'jp_005',                     # Japanese - Female 3
    'jp_006',                     # Japanese - Male
    'kr_002',                     # Korean - Male 1
    'kr_003',                     # Korean - Female
    'kr_004',                     # Korean - Male 2

    # SINGING VOICES
    'en_female_f08_salut_damour',  # Alto
    'en_male_m03_lobby',           # Tenor
    'en_female_f08_warmy_breeze',  # Warmy Breeze
    'en_male_m03_sunshine_soon',   # Sunshine Soon

    # OTHER
    'en_male_narration',           # narrator
    'en_male_funny',               # wacky
    'en_female_emotional',         # peaceful
]

ENDPOINTS = ['https://tiktok-tts.weilnet.workers.dev/api/generation', "https://tiktoktts.com/api/tiktok-tts"]
current_endpoint = 0
# in one conversion, the text can have a maximum length of 300 characters
TEXT_BYTE_LIMIT = 300

# create a list by splitting a string, every element has n chars
def split_string(string: str, chunk_size: int) -> list[str]:
    words = string.split()
    result = []
    current_chunk = ''
    for word in words:
        if len(current_chunk) + len(word) + 1 <= chunk_size:  # Check if adding the word exceeds the chunk size
            current_chunk += ' ' + word
        else:
            if current_chunk:  # Append the current chunk if not empty
                result.append(current_chunk.strip())
            current_chunk = word
    if current_chunk:  # Append the last chunk if not empty
        result.append(current_chunk.strip())
    return result

# checking if the website that provides the service is available
def get_api_response() -> requests.Response:
    url = f'{ENDPOINTS[current_endpoint].split("/a")[0]}'
    response = requests.get(url)
    return response

# saving the audio file
def save_audio_file(base64_data: str, filename: str = "output.mp3") -> None:
    audio_bytes = base64.b64decode(base64_data)
    with open(filename, "wb") as file:
        file.write(audio_bytes)

# send POST request to get the audio data
def generate_audio(text: str, voice: str) -> bytes:
    url = f'{ENDPOINTS[current_endpoint]}'
    headers = {'Content-Type': 'application/json'}
    data = {'text': text, 'voice': voice}
    response = requests.post(url, headers=headers, json=data)
    return response.content

# creates an text to speech audio file
def tts(text: str, voice: str = "none", filename: str = "output.mp3", play_sound: bool = False) -> None:
    # checking if the website is available
    global current_endpoint

    if get_api_response().status_code == 200:
        print("Service available!")
    else:
        current_endpoint = (current_endpoint + 1) % 2
        if get_api_response().status_code == 200:
            print("Service available!")
        else:
            print(f"Service not available and probably temporarily rate limited, try again later...")
            return
    
    # checking if arguments are valid
    if voice == "none":
        print("No voice has been selected")
        return
    
    if not voice in VOICES:
        print("Voice does not exist")
        return

    if len(text) == 0:
        print("Insert a valid text")
        return

    # creating the audio file
    try:
        if len(text) < TEXT_BYTE_LIMIT:
            audio = generate_audio((text), voice)
            if current_endpoint == 0:
                audio_base64_data = str(audio).split('"')[5]
            else:
                audio_base64_data = str(audio).split('"')[3].split(",")[1]
            
            if audio_base64_data == "error":
                print("This voice is unavailable right now")
                return
                
        else:
            # Split longer text into smaller parts
            text_parts = split_string(text, 299)
            audio_base64_data = [None] * len(text_parts)
            
            # Define a thread function to generate audio for each text part
            def generate_audio_thread(text_part, index):
                audio = generate_audio(text_part, voice)
                if current_endpoint == 0:
                    base64_data = str(audio).split('"')[5]
                else:
                    base64_data = str(audio).split('"')[3].split(",")[1]

                if audio_base64_data == "error":
                    print("This voice is unavailable right now")
                    return "error"
            
                audio_base64_data[index] = base64_data

            threads = []
            for index, text_part in enumerate(text_parts):
                # Create and start a new thread for each text part
                thread = threading.Thread(target=generate_audio_thread, args=(text_part, index))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Concatenate the base64 data in the correct order'


            audio_base64_data = "".join(audio_base64_data)
            
        save_audio_file(audio_base64_data, filename)
        print(f"Audio file saved successfully as '{filename}'")
        if play_sound:
            playsound(filename)

    except Exception as e:
        print("Error occurred while generating audio:", str(e))

def speed_up_audio(input_path, output_path, speed=1.5):
    # Load the audio file
    audio = AudioSegment.from_file(input_path)

    # Speed up the audio file
    sped_up_audio = audio.speedup(playback_speed=speed)

    # Export the sped-up audio file
    sped_up_audio.export(output_path, format="mp3")

text = 'Once upon a time, in a small coastal town named Harborville, there lived a young woman named Amelia. Amelia had always felt a deep connection to the sea, and she spent her days collecting seashells, watching the waves, and dreaming of adventures on the open water. One sunny morning, as Amelia strolled along the beach, she stumbled upon a mysterious bottle half-buried in the sand. Curiosity piqued, she reached down and pulled it out. Inside the bottle was a weathered piece of parchment with a message written in elegant script. It read: "To the one who finds this message, know that you are destined for greatness. Seek the fabled Lost Island of Serenity, and you shall find treasure beyond your wildest dreams. Trust in your heart and the guidance of the sea." Amelias heart raced with excitement. The idea of embarking on a grand adventure filled her with a sense of purpose she had never felt before. She rushed home to gather supplies, including food, water, a map, and her trusty compass. With a firm resolve, she set off on her journey, leaving a note for her family to let them know she would be back soon. Days turned into weeks as Amelia sailed through stormy seas, navigating treacherous waters, and encountering strange creatures of the deep. At night, she would gaze at the stars, relying on them to guide her in the right direction. The journey was tough, but Amelias determination and love for the sea kept her going. Finally, one misty morning, she spotted land on the horizon. As she drew closer, she realized that she had arrived at a lush, verdant island surrounded by clear turquoise waters. This must be the Lost Island of Serenity, she thought. Her heart swelled with anticipation. Amelia rowed ashore and explored the island, marveling at its breathtaking beauty. She discovered exotic plants, colorful birds, and crystal-clear streams that flowed through the heart of the island. As she ventured deeper into the jungle, she stumbled upon an ancient temple covered in moss and vines. Inside the temple, she found a chamber filled with treasure beyond her wildest dreams - chests of gold, precious gems, and artifacts from long-lost civilizations. But what truly caught her eye was a simple, yet exquisite, seashell necklace resting on a stone pedestal. It glimmered with an inner light, and Amelia knew that it was the true treasure she had been searching for. As she picked up the necklace, a voice whispered in her ear, "You have passed the test, Amelia. The real treasure is not gold or gems but the beauty of the world around you and the courage in your heart." With the seashell necklace around her neck, Amelia felt a sense of fulfillment she had never known before. She knew that her journey had not only brought her material wealth but had also enriched her soul. She spent several days exploring the island, taking in its wonders and learning about its history. When it was time to leave, Amelia knew that she would carry the memories of her adventure with her forever. She sailed back to Harborville, where her family welcomed her with open arms. She shared her tale of the Lost Island of Serenity and the lessons she had learned along the way. Amelia continued to live by the sea, but her heart was now filled with a deep sense of gratitude and contentment. She knew that the greatest treasure of all was the beauty of the world and the courage to chase her dreams, and she cherished every moment of her life by the sea, knowing that the greatest adventures could be found in the simplest of things.'
voice = "en_us_007" # all possible voices can be found here

# arguments:
#   - input text
#   - vocie which is used for the audio
#   - output file name
#   - play sound after generating the audio
tts(text, voice, "output.mp3", play_sound=False)


input_audio_path = 'output.mp3'  # Replace with your audio file path
output_audio_path = 'new.mp3'   # Replace with the desired output file path
speed_factor = 1.2  # Increase the speed by 1.5 times

speed_up_audio(input_audio_path, output_audio_path, speed=speed_factor)

# To play the sped-up audio (optional)
sped_up_audio = AudioSegment.from_file(output_audio_path)