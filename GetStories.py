import praw
import os
import random
import re
from VidUtils import gpt

env = {
    'CLIENT_ID' : "",
    'CLIENT_SECRET' : "",
    "USER_AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "OPENAI_API_KEY" : "",
}

class Scraper:
    def __init__(self, env, subreddits):
        self.env = env
        self.subreddits = subreddits
        self.gpt = gpt.GPT(env)
        # Read-only instance
        self.reddit = praw.Reddit(client_id=env['CLIENT_ID'],
                                  client_secret=env['CLIENT_SECRET'],
                                  user_agent=env['USER_AGENT'])
        self.reddit.read_only = True
        self.minLength = 2000
        self.minPost = 400
        self.maxPost = 2000

    def correctSpacing(self, story):
        paragraphs = [paragraph for paragraph in story.split('\n') if paragraph.strip()]
        output = []
        i = 0
        for paragraph in paragraphs:
            for i in range(len(paragraph)):
                if paragraph[i] == '.' and i + 1 < len(paragraph):
                    if paragraph[i+1] != ' ' and paragraph[i+1] != '.' and paragraph[i+1] != '"' and paragraph[i+1] != "'" and not paragraph[i+1].isdigit():
                        # print(paragraph[i], paragraph[i+1])
                        paragraph = paragraph[:i+1] + ' ' + paragraph[i+1:]
                elif paragraph[i] == '?' and i + 1 < len(paragraph):
                    if paragraph[i+1] != ' ' and paragraph[i+1] != '.' and paragraph[i+1] != '"' and paragraph[i+1] != "'" and not paragraph[i+1].isdigit():
                        # print(paragraph[i], paragraph[i+1])
                        paragraph = paragraph[:i+1] + ' ' + paragraph[i+1:]
                elif paragraph[i] == '!' and i + 1 < len(paragraph):
                    if paragraph[i+1] != ' ' and paragraph[i+1] != '.' and paragraph[i+1] != '"' and paragraph[i+1] != "'" and not paragraph[i+1].isdigit():
                        # print(paragraph[i], paragraph[i+1])
                        paragraph = paragraph[:i+1] + ' ' + paragraph[i+1:]

            output.append(paragraph)

        return '\n'.join(output)

    def gradeStories(self, folder_path):
        print("Creating summary of stories chosen")
        
        summary = []
        final = ""

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf8') as file:
                    text = file.read()
                summary.append(['Char Count: ' + str(len(text)), 'Title: ' + text.split("\n\n\n\n")[0], 'Problems: \n' + self.gpt.check(text)])

        summaries = ""
        for i,story in enumerate(summary):
            summaries += f"{i+1} : {story[1]}\n\n"

        summary.insert(0, ['Order:'+self.gpt.grade(summaries)])

        for i,story in enumerate(summary):
            if i != 0:
                final+=f'{i}.\n'
            for aspect in story:
                final+=aspect+'\n'

            final+= '\n\n'


        file_path = os.path.join(folder_path, '0.txt')
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(final)

    def getStories(self, folder):
        totalChars = 0
        totalStories = 0

        storyDir = os.path.join(os.getcwd(), folder)

        # create story folder if not already there
        if not os.path.isdir(storyDir):
            os.mkdir(storyDir)
        # if there is a story folder see how many chars are already found
        else:
            for filename in os.listdir(storyDir):
                if filename.endswith('.txt') and filename[0] != '0':
                    filename = os.path.join(storyDir, filename)
                    with open(filename, 'r', encoding='utf8') as file:
                        text = file.read()
                        totalChars += len(text)
                    totalStories += 1


        while totalChars < self.minLength:
            # 0 - title, 1 - text, 2 - char count
            totalStories += 1
            story = self.getHotPost()

            if story[0] == 'no stories':
                print("No more stories to search on reddit buddy")
                exit()

            totalChars += story[2]

            # save story to a folder
            with open(storyDir + '/' + f"{totalStories}.txt", 'w', encoding='utf8') as file:
                file.write(story[1])
        if not os.path.exists(storyDir + "/0.txt"):
            self.gradeStories(storyDir)


    def getHotPost(self):
        post = None
        past_titles = set()

        with open('media/past-stories.txt', 'r', encoding='utf8') as file:
            for line in file:
                past_titles.add(line.strip())

        subredditName = random.choice(self.subreddits)
        subreddit = self.reddit.subreddit(subredditName)
        minPostLength = self.minPost
        maxPostLength = self.maxPost
        
        print(f"Finding Posts in {subredditName}...")
        for hotPost in subreddit.hot():
            if hotPost.is_self and hotPost.title not in past_titles and (minPostLength < len(hotPost.selftext) < maxPostLength):
                try:
                    print(f"Checking contents of: {hotPost.title}\n")
                except UnicodeEncodeError as e:
                    print(f"title has bad char: {e}")
                if self.gpt.checkStory(hotPost.selftext):
                    print(f'VALID STORY')
                    past_titles.add(hotPost.title)
                    post = hotPost
                    break
                else:
                    past_titles.add(hotPost.title)
                    print("Story Content No Good")

        if not post:
            for hotPost in subreddit.new():
                if hotPost.is_self and hotPost.title not in past_titles and (minPostLength <= len(hotPost.selftext) <= maxPostLength):
                    try:
                        print(f"Checking contents of: {hotPost.title}\n")
                    except UnicodeEncodeError as e:
                        print(f"An error occurred while printing the title: {e}")
                    if self.gpt.checkStory(hotPost.selftext):
                        print(f'VALID STORY')
                        past_titles.add(hotPost.title)
                        post = hotPost
                        break
                    else:
                        past_titles.add(hotPost.title)
                        print("Story Content No Good")
        if not post:
            print(f"No Post found matching those criteria in {subredditName}")
            self.subreddits.remove(subredditName)
            if len(self.subreddits) > 0:
                return self.getHotPost()
        
        with open('media/past-stories.txt', 'w', encoding='utf8') as file:
            file.write("\n".join(list(past_titles)))

        print("Moderating.....")
        post.title = self.gpt.createTitle(post.selftext).strip()
        

        print(f"New Title: {post.title}")
        paragraphs = [paragraph for paragraph in post.selftext.split('\n') if paragraph.strip()]

        finalStory = ""
        for i,paragraph in enumerate(paragraphs):
            print(f'On Paragraph {i+1}')
            paragraph = self.gpt.moderate(paragraph).strip().replace('(','').replace(')','').replace('’', "'")
            # finalStory += self.gpt.expandAcronymsAndAbbreviations(paragraph).strip()+'\n'
            finalStory += paragraph
        finalStory = self.correctSpacing(finalStory)
        print("Done Moderation\n")

        return (post.title, post.title+"\n\n\n\n"+finalStory, len(finalStory))


if __name__ == '__main__':
    # Number of videos
    # AITA for disinviting my cousin from my wedding cause of him spreading lies about me to my fiance ?
    videos = 4
    for i in range(videos):
        print(f"------------------------On Video {i+1}------------------------")
        subreddits = []
        
        reddit = Scraper(env, subreddits)

        reddit.getStories(f"tempFiles/Video-{i+1}")

