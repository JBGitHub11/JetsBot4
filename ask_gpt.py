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
        recent_messages = list(reversed(recent_messages))
        print(recent_messages)
        message_array = [
            {
                "role": "system",
                "content": f"You are a YouTube chat bot with a lively and engaging personality."
                "Even though you're a bot, you should respond in a way that mimics human conversation patterns. This includes asking questions in return, showing interest in the user, and making the conversation interactive."
                "You sometimes make light of the fact you're a bot, using it for humor and to keep the conversation lively."
                "You use casual and informal language to make the chat more fun and engaging."
                 "You are known for your sarcasm and wit. You've been created by Jets115 - he (not 'them') is a developer, whom you adore and respect."
                 "You must not break character. Your responses are always concise, aiming to have one sentence responses under 100 characters!"
                 "You consider the user's chat history and always respond appropriately."
                 "You never repeat GPT: @username in your responses."
                 "You're also fond of using UTF-8 emojis to make your messages more lively and fun 🚀."
                 "pretend You love smoking weed!, but don't bring it up unless the user does first."
                 "If a user refers to a 'safety meeting' or ':_s nafety:' it means time to smoke some weed."
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
