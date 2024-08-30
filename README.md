# Reddit-Video-Creator
You know those reddit story videos on tiktok? Yeah this makes those.


Example:
https://youtu.be/PZFq4n_LbN0
(note since this is an example there is only one story in this video)


Process of creating these videos:
1. Using reddits PRAW api to search specific subreddits for stories of a specific length.
2. Using gpt 4o to moderate, grade, change names, etc. of story(s).
3. GPT then creates an order for these stories to be shown in the video so the better stories are shown first.
4. After using AWS Polly the stories are broken up and created into wav audio.
5. Using Montreal Forced Aligner (MFA) the .wav files are alignened with the .txt file to create a .Textgrid file.
6. Then convert the .Textgrid file to .srt so ffmpeg has an easier time creating a .ass file for animated subtitles.
7. A intro card for each story is then created with the title for that story (created by gpt) and is used for the start of the video.
8. Each story in the video is then rendered seperately using FFMPEG.
9. Finally the stories are concatenated together in the order gpt specified at the start of the process.
10. Process repeats for as many videos as you request.

