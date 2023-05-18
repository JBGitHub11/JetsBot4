import argparse
from youtube_manager import YouTubeChat
from database_manager import DatabaseManager
from ask_gpt import GPTChatBot
import pytchat
import time
import random
import configparser
import codecs
import unicodedata
from colorama import Fore, init
init()

def main():
    with codecs.open('config.ini', 'r', encoding='utf-8') as f:
        config = configparser.ConfigParser()
        config.read_file(f)
    admin_users = config.get('Admins', 'users').split(',')
    banned_users = [user for user, banned in config.items('banned_users') if banned.lower() == 'true']
    
    gg_message_list = [v for k, v in config.items('gg_messages')]
    gg_authors = {}
    gg_mention_window = 300  # 5 minutes
    gg_message_cooldown = 1200  # 20 minutes
    last_gg_response_time = 0  

    safety_meeting_messages = [v for k, v in config.items('safety_meeting_messages')]
    safety_meeting_mentions = {}
    last_safety_message_time = 0
    safety_message_cooldown = 60 * 20  # 20 minutes
    safety_mention_window = 60 * 5  # 5 minutes

    # Slava tracking
    slava_messages = [v for v in config["slava_messages"].values()]
    slava_mentions = {}
    last_slava_message_time = 0
    slava_message_cooldown = 60 * 20  # Twenty minutes in seconds
    slava_mention_window = 2 * 60  # Two minutes in seconds

    should_continue = True
    user_last_message_times = {}

    parser = argparse.ArgumentParser(description='Process video ID.')
    parser.add_argument('--videoid', type=str, help='The ID of the YouTube video to process')
    parser.add_argument('--silent', action='store_true', help='If set, no messages will be sent to YouTube.')
    parser.add_argument("--restrict",type=int,default=0,help="Restrict users to sending a message every N seconds",)
    args = parser.parse_args()
    video_id = args.videoid
    silent = args.silent
    print(f'Processing video ID: {video_id}')

    db_manager = DatabaseManager('jetsbot_memory.db')
    db_manager.create_tables()

    youtube_chat = YouTubeChat(db_manager, 'client_secret.json', 'token.pickle', ["https://www.googleapis.com/auth/youtube.force-ssl"], silent)
    gpt_chat_bot = GPTChatBot(db_manager)

    live_chat_id = youtube_chat.get_live_chat_id(video_id)
    chat = pytchat.create(video_id=video_id)


    # Send the startup message
    if args.restrict:
        youtube_chat.send_live_chat_message(
            live_chat_id,
            f"✈️🤖 JetsBotv4 Live 🟢! Use '[!gpt] {{your text}}'. Slow mode on 🐢: 1 chat every {args.restrict} min. Wipe chats with '!gpt forget me' Feedback: https://forms.gle/DWrGcBCEXofu5TNg8."
        )
    else:
        youtube_chat.send_live_chat_message(
            live_chat_id,
            "✈️🤖 JetsBotv4 Ready 🟢! Use '[!gpt] {your text}'. Reset our chat with '!gpt forget me'. Let's talk! Feedback: https://forms.gle/DWrGcBCEXofu5TNg8"
        )





    while chat.is_alive() and should_continue:
        for c in chat.get().sync_items():            
            message_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c.timestamp/1000.0))  # Convert the timestamp to a readable format
            if 'jets' in c.author.name.lower() or 'jets' in c.message.lower():
                print(Fore.GREEN + f"{message_time} - {c.author.name}: {c.message}")
            else:
                print(Fore.WHITE + f"{message_time} - {c.author.name}: {c.message}")

            author_name = c.author.name
            if c.author.name.lower() in banned_users:
                print(f"Ignoring message from banned user: {c.author.name}")
                continue
            if c.message.lower() == '!gpt forget me':
                deletion_success = db_manager.delete_user_messages(c.author.name)
                if deletion_success:
                    youtube_chat.send_live_chat_message(live_chat_id, f"GPT: @{c.author.name[:10]} Your data has been deleted. 🗑️")
                else:
                    youtube_chat.send_live_chat_message(live_chat_id, f"GPT: @{c.author.name[:10]} Error deleting your data. Please try again. 😓")
                continue
            if c.author.name in admin_users:
                if c.message.startswith('!gpt stats'):
                    # Process the '!gpt stats' command
                    stats = db_manager.get_db_stats()
                    youtube_chat.send_live_chat_message(live_chat_id, stats)
                    continue
                elif c.message.startswith('!gpt truncate'):
                    # Process the '!gpt truncate' command
                    db_manager.truncate_table('messages')
                    youtube_chat.send_live_chat_message(live_chat_id, "Table truncated." + db_manager.get_db_stats())
                    continue
                elif c.message.startswith('!gpt shutdown'):
                    should_continue = False
                    shutdown_messages = [
                        config.get("shutdown_messages", key)
                        for key in config.options("shutdown_messages")
                    ]

                    shutdown_message = random.choice(shutdown_messages)
                    youtube_chat.send_live_chat_message(live_chat_id, shutdown_message)
                    break
                elif c.message.startswith('!gpt restrict'):
                    # Process the '!gpt restrict' command
                    try:
                        new_restrict_value = int(c.message.split()[2])
                        args.restrict = new_restrict_value
                        print(f"Restrict value updated to {new_restrict_value}")
                        if new_restrict_value == 0:
                            youtube_chat.send_live_chat_message(live_chat_id, "Restrict value updated to 0. Users can now send messages without any delay.")
                        else:
                            youtube_chat.send_live_chat_message(live_chat_id, f"Restrict value updated to {new_restrict_value} minutes. Users can now send a message every {new_restrict_value} minutes.")
                    except (IndexError, ValueError):
                        print("Invalid restrict command. Usage: '!gpt restrict <value>'")
                    continue



                # Add more admin commands here as needed
            
            if c.message.startswith('!gpt'):
                 # Check if the user is allowed to send a message
                if c.author.name in user_last_message_times:
                    time_since_last_message = time.time() - user_last_message_times[c.author.name]
                    if time_since_last_message < args.restrict * 60:  # Convert restrict from minutes to seconds
                        time_left = args.restrict * 60 - time_since_last_message
                        print(f"Ignoring message from {c.author.name} due to restriction. They can send a message in {time_left:.2f} seconds.")
                        continue

                # Update the time of the user's last message
                user_last_message_times[c.author.name] = time.time()

                question = c.message[4:].strip()  # Remove '!gpt' from the start of the message

                # Remove control characters from the question and replace new lines with a space
                question = "".join(ch if unicodedata.category(ch)[0]!="C" else ' ' for ch in question)

                answer = gpt_chat_bot.ask_gpt(question, c.author.name)
                print(f"Response from OpenAI: {answer}")  # Print the response from OpenAI

                # Remove control characters from the answer and replace new lines with a space
                answer = "".join(ch if unicodedata.category(ch)[0]!="C" else ' ' for ch in answer)

                # Truncate the answer at the last punctuation mark within 190 characters
                if len(answer) > 190:
                    truncated_answer = answer[:190]
                    last_punctuation = max(truncated_answer.rfind(ch) for ch in '.!?')
                    if last_punctuation != -1:
                        answer = truncated_answer[:last_punctuation + 1]
                    else:
                        answer = truncated_answer

                db_manager.store_message("user", c.author.name, question, answer)
                if not silent:
                    youtube_chat.send_live_chat_message(live_chat_id, answer)
            
            if c.message.lower() == 'gg':
                # Update the time of the last 'gg' message for the author
                gg_authors[c.author.name] = time.time()

                # Remove authors whose 'gg' message is older than the gg_mention_window
                gg_authors = {author: timestamp for author, timestamp in gg_authors.items() if time.time() - timestamp <= gg_mention_window}

                print(f"gg_authors after filtering: {gg_authors}")  # Debug print

                # If there are at least 3 unique 'gg' authors in the last gg_mention_window and the cooldown has passed
                if len(gg_authors) >= 3 and time.time() - last_gg_response_time > gg_message_cooldown:
                    # Select a random message from the gg_messages
                    random_message = random.choice(gg_message_list)

                    print(f"Sending gg message: {random_message}")  # Debug print

                    # Send the message to YouTube
                    youtube_chat.send_live_chat_message(live_chat_id, random_message)

                    # Update the time of the last 'gg' response
                    last_gg_response_time = time.time()

                    # Clear the list of 'gg' authors
                    gg_authors.clear()


            # Check if the message contains 'safety meeting' or ':_safety:' and the cooldown has passed
            if ("safety meeting" in c.message.lower() or ":_safety:" in c.message.lower()) and time.time() - last_safety_message_time > safety_message_cooldown:
                # Update the timestamp of the 'safety meeting' message from this user
                safety_meeting_mentions[c.author.name] = time.time()

                # Remove users whose 'safety meeting' message is older than the safety_mention_window
                safety_meeting_mentions = {user: t for user, t in safety_meeting_mentions.items() if time.time() - t <= safety_mention_window}

                # If there are at least 2 unique users who mentioned 'safety meeting' in the last safety_mention_window
                if len(safety_meeting_mentions) >= 3:
                    # Select a random message from the safety_meeting_messages
                    random_message = random.choice(safety_meeting_messages)

                    # Send the message to YouTube
                    youtube_chat.send_live_chat_message(live_chat_id, random_message)

                    # Update the time of the last 'safety meeting' message
                    last_safety_message_time = time.time()

                    # Clear the dictionary of 'safety meeting' messages
                    safety_meeting_mentions.clear()

            if ("slava ukraini" in c.message.lower() or "slava ukraine" in c.message.lower()) and time.time() - last_slava_message_time > slava_message_cooldown:
                if (
                    author_name not in slava_mentions
                    or time.time() - slava_mentions[author_name]
                    > slava_mention_window
                ):
                    slava_mentions[
                        author_name
                    ] = time.time()  # Add or update the author's mention time
                if (
                    len(
                        [
                            user
                            for user, mention_time in slava_mentions.items()
                            if time.time() - mention_time < slava_mention_window
                        ]
                    )
                    >= 2
                ):
                    message = random.choice(
                        slava_messages
                    )  # Choose a random Slava Ukraini! message
                    youtube_chat.send_live_chat_message(live_chat_id, message)
                    last_slava_message_time = time.time()
                    slava_mentions = (
                        {}
                    )  # Reset the dictionary after sending a message
    youtube_chat.send_live_chat_message(live_chat_id, "GPT: Status: 🔴", )






if __name__ == "__main__":
    main()
