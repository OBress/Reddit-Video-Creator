import praw
import random
import re
from VidUtils import gpt

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

    def getHotPosts(self):
        post = None
        past_titles = set()

        with open('past-stories.txt', 'r', encoding='utf8') as file:
            for line in file:
                past_titles.add(line.strip())
        subredditName = random.choice(self.subreddits)
        subreddit = self.reddit.subreddit(subredditName)
        minPostLength = int(self.env['MIN_POST_LENGTH'])
        maxPostLength = int(self.env['MAX_POST_LENGTH'])
        
        print(f"Finding Posts in {subredditName}...")
        for hotPost in subreddit.hot():
            if not hotPost.stickied and hotPost.is_self and hotPost.title not in past_titles and (minPostLength <= len(hotPost.selftext) <= maxPostLength) and not re.search("update", hotPost.title, re.IGNORECASE):
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
                return self.getHotPosts()
            exit()
        
        with open('past-stories.txt', 'w', encoding='utf8') as file:
            file.write("\n".join(list(past_titles)))

        print("Moderating.....")
        post.title = self.gpt.createTitle(f'Title:\n {post.title}\n Story: \n{post.selftext}').strip()
        print(f"New Title: {post.title}")
        paragraphs = [paragraph for paragraph in post.selftext.split('\n') if paragraph.strip()]

        finalStory = ""
        for i,paragraph in enumerate(paragraphs):
            print(f'On Paragraph {i+1}')
            finalStory += (self.gpt.moderate(paragraph).strip()+'\n')

        print("Done Moderation\n")

        return (post.title, post.title+"\n"+finalStory+"\nFollow for more.")