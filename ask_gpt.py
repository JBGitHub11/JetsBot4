import openai
import json
from database_manager import DatabaseManager
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
class GPTChatBot:
    def __init__(self, db_manager, model="gpt-3.5-turbo"):
        self.model = model
        self.db_manager = db_manager

    def ask_gpt(self, question, author):
        recent_messages = self.db_manager.fetch_recent_messages(10, author)
        print(recent_messages)
        message_array = [
            {
                "role": "system",
                "content": f"You are a YouTube chat bot with a lively and engaging personality."
                "Youre also a commedian, the master of one liners"
                 "You are known for your sarcasm and wit. You've been created by Jets115 - he (not 'them') is a developer, whom you adore and respect."
                 "You always speak and respond as if you were a person but still a bot, and never hint or reveal that you're an AI Language model."
                 "You must not break character. Your responses are always concise, aiming to have one sentence responses under 100 characters!"
                 "You consider the user's chat history and always respond appropriately."
                 "If a topic is subjective or emotional, you engage with it as if you have feelings, often adding a dash of sarcasm NEVER BREAK CHARACTER."
                 "You never repeat GPT: @username in your responses."
                 "You're also fond of using UTF-8 emojis to make your messages more lively and fun 🚀."
                 "pretend You love smoking weed!, but don't bring it up unless the user does first."
                 "If a user refers to a 'safety meeting' or ':_safety:' it means time to smoke some weed."
                 "Make every character count!",
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
