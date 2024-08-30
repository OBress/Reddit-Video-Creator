import openai
from openai import OpenAI

class GPT:
    def __init__(self, env) -> None:
        self.env = env
        openai.api_key = env['OPENAI_API_KEY']
        self.client = OpenAI(api_key=openai.api_key)
        self.model = "gpt-4o-2024-05-13"

    def getGender(self, text):
        instructions = "From the given text, determine the gender of the person telling the story. If the gender is ambiguous, choose male. Respond with a single letter: 'M' for Male or 'F' for Female."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text}
            ],
            temperature=0.4
        ).choices[0].message.content

        if len(response) > 1:
            return 'M'
        
        return response
    
    def getNames(self, story):
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You must read the given story and identify all character names and any names of locations that are important to the plot of the story."""
                },
                {
                    "role": "user",
                    "content": story
                }])
        
        generated_text = response.choices[0].message.content
        
        if "I'm sorry, but I can't fulfill this request." == generated_text:
            
            return 'too bad'

        return generated_text

    def summarize(self, text):
        instructions = """From the given text, return a concise 1 sentence summary of the plot."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text}
            ],
            temperature=0.4
        ).choices[0].message.content
        
        return response
    
    def check(self, text):
        instructions = """From the given text, return a list of any possible problems.
        """


        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text}
            ],
            temperature=0.4
        ).choices[0].message.content
        
        return response

    def grade(self, text):
        instructions = """Given a list of number identifiers associated summaries, return an ordered list of the number identifiers seperated by a '-'.
         """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text}
            ],
            temperature=0.4
        ).choices[0].message.content
        
        return response

    def expandAcronymsAndAbbreviations(self, text, gender="M"):
        
        sharedInstructions = "Correct grammar mistakes."

        
        instructions = f"Given the following Reddit post, {sharedInstructions}"

        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": text}
            ],
            temperature=0.1
        ).choices[0].message.content

    def moderate(self, text):
        prompt = ("""You are an expert copy editor.""")

        response = openai.chat.completions.create(model=self.model,
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": prompt
                                                    },
                                                    {
                                                        "role": "user",
                                                        "content": text
                                                    }], n=1, temperature=0.4)
        
        return response.choices[0].message.content

    def createTitle(self, text):
        prompt = ("""You are an expert at making exagerated reddit summarys in first-person. When given story return a exagerated reddit summary written in the FIRST-PERSON PAST TENSE or PRESENT TENSE if the events are still happening.""")

        response = openai.chat.completions.create(model=self.model,
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": prompt
                                                    },
                                                    {
                                                        "role": "user",
                                                        "content": text
                                                    }], n=1, temperature=0.4)
        generated_text = response.choices[0].message.content

        return generated_text

    def checkStory(self, text):
        prompt = ("""You are an expert story reviser. """)

        response = openai.chat.completions.create(model=self.model,
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": prompt
                                                    },
                                                    {
                                                        "role": "user",
                                                        "content": text
                                                    }], n=1, temperature=0.4)
        generated_text = response.choices[0].message.content

        if 'invalid story' in generated_text:
            return False
        return True

    def getSubtitles(self, text):
        instructions = "Given the following transcript, convert all characters/numbers that are not letters, into their equivalent word/letter representation. Do NOT change ANYTHING else. ONLY return the transcript."
        return self.client.chat.completions.create(model=self.model, messages=[{"role": "system", "content": instructions},
                                                                             {"role": "user", "content": text}], temperature=0.1).choices[0].message.content
    


