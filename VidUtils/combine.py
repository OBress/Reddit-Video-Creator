import os
import subprocess
import ffmpeg

def get_order(order_location):
    # Get order of the videos to be concatinated
    print(order_location)
    with open(order_location, 'r', encoding='utf8') as file:
        order = file.read()
        # Get first line
        order = order.split('\n')[0]
        # Get order like this 1-2-3
        order = order.split(':')[1]
        # get final order
        order = order.split('-')
    
    return order

def getVideoStream(videoProbe):
    return next((stream for stream in videoProbe['streams'] if stream['codec_type'] == 'video'), None)


def create_stuff(order, videos, location, title_location):
    # DESCRIPTION and TITLE
    num = 1
    desciption = "Hope you enjoyed todays video! Leave your thoughts down below in the comments. Everything in our videos is owned/licensed by me. 👍\n\n"
    videoDuration = 0.0

    for ord in order:

        # Convert duration to minutes and seconds
        minutes = int(videoDuration // 60)
        seconds = int(videoDuration % 60)

        # Format the duration
        formattedDuration = f"{minutes}:{seconds:02d}"
        desciption += f"Story {num} - {formattedDuration}\n"

        # TITLE
        if num == 1:
            with open(title_location+f'{ord}.txt', encoding='utf8') as file:
                title = file.read().split('\n\n\n\n')[0]

            with open(location+'title.txt', 'w', encoding='utf8') as file:
                file.write(title)
        # print(num)
        videoProbe = ffmpeg.probe(videos[int(ord)-1])
        videoStream = getVideoStream(videoProbe)
        videoDuration += float(videoStream['duration'])
        num += 1
            

    desciption += """\n\nHow do I make these videos?
1. My writer with a BA in English Literature and certificate in creative writing develops and edits the stories used.
2. I give feedback if necessary on the stories until it is up to par with my quality standard.
3. I then put together licensed footage and the voice overs into a video editor while adding any final touches to the video.
4. Last but not least we review the final video in it's entirety and confirm it's well above the standard."""

    with open(location+'description.txt', 'w', encoding='utf8') as file:
        file.write(desciption)





def concatenate_videos_in_folder(folder_path, output_filename, order_location, title_location):
    # Create a temporary file to hold the list of videos
    
    videos = []

    # Get all video paths in numerical order
    for i, filename in enumerate(sorted(os.listdir(folder_path+'temp'))):
        if filename.endswith('.mp4'):
            videos.append(os.path.join(folder_path+'temp', filename))

    # Get order of the videos to be concatinated
    order = get_order(order_location)

    with open('video_list.txt', 'w') as file_list:
        for ord in order:
            file_list.write(f"file '{videos[int(ord)-1]}'\n")

    create_stuff(order, videos, folder_path, title_location)
    

    # Run ffmpeg to concatenate the videos
    ffmpeg_command = [
    'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'video_list.txt', 
    '-c:v', 'h264_nvenc', '-b:v', '50000k', '-preset', 'medium', '-c:a', 'aac', output_filename
    ]

    subprocess.run(ffmpeg_command)

    
    # Clean up temporary files
    os.remove('video_list.txt')


if __name__ == "__main__":
    folder_path = 'output/Listen By Listening/Video-1/'  # Replace with your folder path
    output_filename = 'final.mp4'       # Replace with your desired output file name
    order_location = f"tempFiles/Video-1/0.txt"
    title_location = f"tempFiles/Video-1/"

    concatenate_videos_in_folder(folder_path, output_filename, order_location, title_location)
