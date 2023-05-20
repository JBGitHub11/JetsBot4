import time
import random
import configparser
import codecs

class EventChecks:
    def __init__(self):
        with codecs.open('config.ini', 'r', encoding='utf-8') as f:
            config = configparser.ConfigParser()
            config.read_file(f)

        self.gg_message_list = [v for k, v in config.items('gg_messages')]
        self.gg_authors = {}
        self.gg_mention_window = 300  # 5 minutes
        self.gg_message_cooldown = 1200  # 20 minutes
        self.last_gg_response_time = 0  

        self.safety_meeting_messages = [v for k, v in config.items('safety_meeting_messages')]
        self.safety_meeting_mentions = {}
        self.last_safety_message_time = 0
        self.safety_message_cooldown = 60 * 20  # 20 minutes
        self.safety_mention_window = 60 * 5  # 5 minutes

        # Slava tracking
        self.slava_messages = [v for v in config["slava_messages"].values()]
        self.slava_mentions = {}
        self.last_slava_message_time = 0
        self.slava_message_cooldown = 60 * 20  # Twenty minutes in seconds
        self.slava_mention_window = 2 * 60  # Two minutes in seconds

    def check_gg_event(self, author_name, message, youtube_chat, live_chat_id):
        if message.lower() == 'gg':
            self.gg_authors[author_name] = time.time()
            self.gg_authors = {author: timestamp for author, timestamp in self.gg_authors.items() if time.time() - timestamp <= self.gg_mention_window}

            if len(self.gg_authors) >= 1 and time.time() - self.last_gg_response_time > self.gg_message_cooldown:
                random_message = random.choice(self.gg_message_list)
                youtube_chat.send_live_chat_message(live_chat_id, random_message)
                self.last_gg_response_time = time.time()
                self.gg_authors.clear()

    def check_safety_event(self, author_name, message, youtube_chat, live_chat_id):
        if ("safety meeting" in message.lower() or ":_safety:" in message.lower()) and time.time() - self.last_safety_message_time > self.safety_message_cooldown:
            self.safety_meeting_mentions[author_name] = time.time()
            self.safety_meeting_mentions = {user: t for user, t in self.safety_meeting_mentions.items() if time.time() - t <= self.safety_mention_window}

            if len(self.safety_meeting_mentions) >= 1:
                random_message = random.choice(self.safety_meeting_messages)
                youtube_chat.send_live_chat_message(live_chat_id, random_message)
                self.last_safety_message_time = time.time()
                self.safety_meeting_mentions.clear()

    def check_slava_event(self, author_name, message, youtube_chat, live_chat_id):
        if ("slava ukraini" in message.lower() or "slava ukraine" in message.lower()) and time.time() - self.last_slava_message_time > self.slava_message_cooldown:
            if (
                author_name not in self.slava_mentions
                or time.time() - self.slava_mentions[author_name]
                > self.slava_mention_window
            ):
                self.slava_mentions[author_name] = time.time()  
            if (
                len(
                    [
                        user
                        for user, mention_time in self.slava_mentions.items()
                        if time.time() - mention_time
                        <= self.slava_mention_window
                    ]
                )
                >= 1
            ):
                random_message = random.choice(self.slava_messages)
                youtube_chat.send_live_chat_message(live_chat_id, random_message)
                self.last_slava_message_time = time.time()
                self.slava_mentions.clear()

