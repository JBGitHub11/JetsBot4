import random

class AdminCommands:
    def __init__(self, db_manager, youtube_chat, live_chat_id, admin_users, config):
        self.db_manager = db_manager
        self.youtube_chat = youtube_chat
        self.live_chat_id = live_chat_id
        self.admin_users = admin_users
        self.config = config

    def process_command(self, command, restrict_value):
        if command.startswith('!gpt stats'):
            stats = self.db_manager.get_db_stats()
            self.youtube_chat.send_live_chat_message(self.live_chat_id, stats)
            return True
        elif command.startswith('!gpt truncate'):
            self.db_manager.truncate_table('messages')
            self.youtube_chat.send_live_chat_message(self.live_chat_id, "Table truncated." + self.db_manager.get_db_stats())
            return True
        elif command.startswith('!gpt shutdown'):
            should_continue = False
            shutdown_messages = [
                self.config.get("shutdown_messages", key)
                for key in self.config.options("shutdown_messages")
            ]

            shutdown_message = random.choice(shutdown_messages)
            self.youtube_chat.send_live_chat_message(self.live_chat_id, shutdown_message)
            return False
        elif command.startswith('!gpt restrict'):
            try:
                new_restrict_value = int(command.split()[2])
                print(f"Restrict value updated to {new_restrict_value}")
                if new_restrict_value == 0:
                    self.youtube_chat.send_live_chat_message(self.live_chat_id, "Restrict value updated to 0. Users can now send messages without any delay.")
                else:
                    self.youtube_chat.send_live_chat_message(self.live_chat_id, f"Restrict value updated to {new_restrict_value} minutes. Users can now send a message every {new_restrict_value} minutes.")
                return new_restrict_value
            except (IndexError, ValueError):
                print("Invalid restrict command. Usage: '!gpt restrict <value>'")
                return restrict_value
        # ...
        return restrict_value
