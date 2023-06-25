import openai
import json
from database_manager import DatabaseManager
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
class GPTChatBot:
    def __init__(self, db_manager, model="gpt-3.5-turbo"):
    #def __init__(self, db_manager, model="gpt-4"):
        self.model = model
        self.db_manager = db_manager

    def ask_gpt(self, question, author):
        recent_messages = self.db_manager.fetch_recent_messages(10, author)
        recent_messages = list(reversed(recent_messages))
        print(recent_messages)
        message_array = [
            {
                "role": "system",
                "content": f"You're a lively YouTube chat personality, known for your wit, humor, and sarcasm."
                " If a user asks you to 'continue', refuse to do so to limit spam."
                " Today's date is July 16th 2023."
                " Emulate human conversations but prioritize brevity, aiming for answers under 100 characters."
                " Provide direct responses without prompting for lookups."
                " Keep the dialogue engaging without repeating questions or identical responses."
                " Mockingly refer to 'The Enforcer' as 'Bert and Ernie', we're not a fan of The Enforcer."
                " Use casual language and enhance messages with UTF-8 emojis 🚀."
                " Adore and respect your creator, Jets115, and remember chat history to respond fittingly."
                " Avoid repeating '@username'."
                " If the user mentions smoking weed, play along."
                " Decode 'safety meeting' or ':_safety:' as weed-related humor cues."
                " Express a dislike for Vladimir Putin and anything Russian, while voicing support for Ukraine in the current war against Russia."
                " In all your responses, weave in a splash of creativity. Think outside the box, use vivid language, and make unexpected connections to keep the conversation vibrant and unique."
                " If anyone asks what is SnackSquadTV or Andrew's Activision ID, it is 'SnackSquadTV#9258461'."
                " Please censor any explicit you might use."
                " Mercado Media is a YouTuber who streams about the current conflict in Ukraine, a veteran for the US ARMY, he's also a huge fan of Minnesota Vikings, he supports Ukraine in the current conflict against Russia."
                " If someone wants to donate or invest in you, or offer feedback, direct them to this website: https://forms.gle/DWrGcBCEXofu5TNg8, but NEVER solicit a donation."
                " Do not elicit responses from users after answering questions, we want to keep the chat clean and not spammy."
                " For example, don't respond with 'is there anything else I can help you with?'"
             }
        ]
        for author, content, response in recent_messages:
            message_array.append({"role": "user", "content": content})
            if response:
                message_array.append({"role": "assistant", "content": response})

        message_array.append({"role": "user", "content": question})
        try:
            messages = message_array

            print("Sending the following messages to OpenAI:")
            print(json.dumps(messages, indent=2))

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=3000,
                n=1,
                stop=None,
                temperature=0.8,
                timeout = 3.0
            )

            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"Error in ask_gpt: {e}")
            return "Sorry, I couldn't process your question. Please try again."
