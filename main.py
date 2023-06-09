import argparse
from youtube_manager import YouTubeChat
from database_manager import DatabaseManager
from ask_gpt import GPTChatBot
import pytchat
import time
import configparser
import codecs
import unicodedata
from colorama import Fore, init
from event_checks import EventChecks
from admin_checks import AdminCommands

init()

def main():
    with codecs.open('config.ini', 'r', encoding='utf-8') as f:
        config = configparser.ConfigParser()
        config.read_file(f)
    admin_users = config.get('Admins', 'users').split(',')
    banned_users = [user for user, banned in config.items('banned_users') if banned.lower() == 'true']
    prefixes = [v for k, v in config.items('prefixes')]
    should_continue = True

    parser = argparse.ArgumentParser(description='Process video ID.')
    parser.add_argument('--videoid', type=str)
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args()
    video_id = args.videoid
    silent = args.silent
    print(f'Processing video ID: {video_id}')

    db_manager = DatabaseManager('jetsbot_memory.db')
    db_manager.create_tables()

    youtube_chat = YouTubeChat(db_manager, 'client_secret.json', 'token.pickle', ["https://www.googleapis.com/auth/youtube.force-ssl"], silent)
    gpt_chat_bot = GPTChatBot(db_manager)

    live_chat_id = youtube_chat.get_live_chat_id(video_id)

    event_checker = EventChecks()
    admin_checks = AdminCommands(db_manager, youtube_chat, live_chat_id, admin_users, config)
    #youtube_chat.send_live_chat_message(live_chat_id,"✈️🤖 JetsBotv4 Ready 🟢! Use '[!gpt] {your text}'. Reset our chat with '!gpt forget me'. Let's talk! Feedback: https://forms.gle/DWrGcBCEXofu5TNg8")
    retry_count = 0
    while retry_count < 3:
        chat = pytchat.create(video_id=video_id)
        while chat.is_alive() and should_continue:
            youtube_chat.refresh_credentials_if_expired()
            for c in chat.get().sync_items():            
                message_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c.timestamp/1000.0))
                if 'jets' in c.author.name.lower() or 'jets' in c.message.lower():
                    print(Fore.GREEN + f"{message_time} - {c.author.name}: {c.message}")
                else:
                    print(Fore.WHITE + f"{message_time} - {c.author.name}: {c.message}")

                # Ignore banned users
                if c.author.name.lower() in banned_users:
                    print(f"Ignoring message from banned user: {c.author.name}")
                    continue

                # Delete user data
                if c.message.lower() == '!gpt forget me':
                    deletion_success = db_manager.delete_user_messages(c.author.name)
                    if deletion_success:
                        youtube_chat.send_live_chat_message(live_chat_id, f"GPT: @{c.author.name[:10]} Your data has been deleted. 🗑️")
                    else:
                        youtube_chat.send_live_chat_message(live_chat_id, f"GPT: @{c.author.name[:10]} Error deleting your data. Please try again. 😓")
                    continue

                admin_commands = ['!gpt stats', '!gpt shutdown', '!gpt truncate']

                # Admin commands
                if c.author.name in admin_users:
                    # Check if the command (without arguments) is in the list of admin commands
                    if c.message.lower() in admin_commands:
                        result = admin_checks.process_command(c.message)
                        if result is False:
                            should_continue = False
                            continue
                        if result is True:
                            continue

                # Chatty Chatbot
                lower_message = c.message.lower()
                if any(lower_message.startswith(prefix.lower()) for prefix in prefixes):
                    message_parts = c.message.split(' ', 1)
                    if len(message_parts) > 1:
                        question = message_parts[1].strip()  # Split only on the first space, so that we get the rest of the sentence
                    else:
                        continue  # If there's no second part, just continue to the next message
                    question = "".join(ch if unicodedata.category(ch)[0]!="C" else ' ' for ch in question)

                    answer = gpt_chat_bot.ask_gpt(question, c.author.name)
                    print(f"Response from OpenAI: {answer}")

                    answer = "".join(ch if unicodedata.category(ch)[0]!="C" else ' ' for ch in answer)

                    if len(answer) > 175:
                        truncated_answer = answer[:175]
                        last_punctuation = max(truncated_answer.rfind(ch) for ch in '.!?')
                        if last_punctuation != -1:
                            answer = truncated_answer[:last_punctuation + 1]
                        else:
                            answer = truncated_answer
                    # Store the message in the database
                    db_manager.store_message("user", c.author.name, question, answer)
                    if not silent:
                        valid_answer = "".join(ch if ch.isprintable() else ' ' for ch in answer)
                        truncated_username = c.author.name[:15]
                        formatted_answer = f"GPT: @{truncated_username} {valid_answer}"
                        youtube_chat.send_live_chat_message(live_chat_id, formatted_answer)

                # Event Checks
                event_checker.check_gg_event(c.author.name, c.message.lower(), youtube_chat, live_chat_id)
                #event_checker.check_safety_event(c.author.name, c.message.lower(), youtube_chat, live_chat_id)
                event_checker.check_slava_event(c.author.name, c.message.lower(), youtube_chat, live_chat_id)

        if not chat.is_alive():
            print("Chat has ended or paused.")
            try:
                chat.raise_for_status()
            except Exception as e:
                print(f"Exception raised: {e}")
            retry_count += 1
        elif not should_continue:
            print("Script was stopped.")
            break
        else:
            print("An unknown error occurred.")
            break
    if retry_count == 3:
        print("Chat connection failed after 3 attempts.")

if __name__ == "__main__":
    main()
