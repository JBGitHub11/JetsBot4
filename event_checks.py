import time
import random
import configparser
import codecs

class EventChecks:
    def __init__(self):
        with codecs.open("config.ini", "r", encoding="utf-8") as f:
            config = configparser.ConfigParser()
            config.read_file(f)

        self.gg_messages = [v for k, v in config.items("gg_messages")]
        self.gg_mentions = {}
        self.gg_mention_window = 60 * 5
        self.gg_message_cooldown = 60 * 20
        self.gg_last_message_time = 0
        self.gg_user_threshold = 3

        self.safety_messages = [v for k, v in config.items("safety_meeting_messages")]
        self.safety_mentions = {}
        self.safety_mention_window = 60 * 5
        self.safety_message_cooldown = 60 * 20
        self.safety_last_message_time = 0
        self.safety_user_threshold = 3

        self.slava_messages = [v for v in config["slava_messages"].values()]
        self.slava_mentions = {}
        self.slava_mention_window = 2 * 60
        self.slava_message_cooldown = 60 * 20
        self.slava_last_message_time = 0
        self.slava_user_threshold = 3

    def check_gg_event(self, author_name, message, youtube_chat, live_chat_id):
        if message.lower() == "gg":
            self.gg_mentions[author_name] = time.time()
            self.gg_mentions = {author: timestamp for author, timestamp in self.gg_mentions.items() if time.time() - timestamp <= self.gg_mention_window}
            if len(self.gg_mentions) >= self.gg_user_threshold and time.time() - self.gg_last_message_time > self.gg_message_cooldown:
                youtube_chat.send_live_chat_message(live_chat_id, random.choice(self.gg_messages))
                self.gg_last_message_time = time.time()
                self.gg_mentions.clear()

    def check_safety_event(self, author_name, message, youtube_chat, live_chat_id):
        if "safety meeting" in message.lower() or ":_safety:" in message.lower() and time.time() - self.safety_last_message_time > self.safety_message_cooldown:
            self.safety_mentions[author_name] = time.time()
            self.safety_mentions = {user: t for user, t in self.safety_mentions.items() if time.time() - t <= self.safety_mention_window}
            if len(self.safety_mentions) >= self.safety_user_threshold:
                youtube_chat.send_live_chat_message(live_chat_id, random.choice(self.safety_messages))
                self.safety_last_message_time = time.time()
                self.safety_mentions.clear()

    def check_slava_event(self, author_name, message, youtube_chat, live_chat_id):
        if "slava ukraini" in message.lower() or "slava ukraine" in message.lower() and time.time() - self.slava_last_message_time > self.slava_message_cooldown:
            if author_name not in self.slava_mentions or time.time() - self.slava_mentions[author_name] > self.slava_mention_window:
                self.slava_mentions[author_name] = time.time()
            if len([user for user, mention_time in self.slava_mentions.items() if time.time() - mention_time <= self.slava_mention_window]) >= self.slava_user_threshold:
                youtube_chat.send_live_chat_message(live_chat_id, random.choice(self.slava_messages))
                self.slava_last_message_time = time.time()
                self.slava_mentions.clear()
