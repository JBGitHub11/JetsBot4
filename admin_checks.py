import random

class AdminCommands:
    def __init__(self, db_manager, youtube_chat, live_chat_id, admin_users, config):
        self.db_manager = db_manager
        self.youtube_chat = youtube_chat
        self.live_chat_id = live_chat_id
        self.admin_users = admin_users
        self.config = config

    def process_command(self, command):
        if command.startswith('!gpt stats'):
            stats = self.db_manager.get_db_stats()
            self.youtube_chat.send_live_chat_message(self.live_chat_id, stats)
            return True
        elif command.startswith('!gpt truncate'):
            self.db_manager.truncate_table('messages')
            self.youtube_chat.send_live_chat_message(self.live_chat_id, "Table truncated." + self.db_manager.get_db_stats())
            return True
        elif command.startswith('!gpt shutdown'):
            shutdown_messages = [
                self.config.get("shutdown_messages", key)
                for key in self.config.options("shutdown_messages")
            ]

            shutdown_message = random.choice(shutdown_messages)
            self.youtube_chat.send_live_chat_message(self.live_chat_id, shutdown_message)
            return False
        