import os
import sqlite3
from sqlite3 import Error
import sys

class DatabaseManager:
    def __init__(self, database_file):
        self.database_file = database_file
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()

    def connect_to_database(self):
        try:
            print("Connecting to the database...")
            conn = sqlite3.connect(self.database_file)
            print("Connected to the database.")
            return conn
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            sys.exit(1)

    def get_db_stats(self):
        try:
            # Get the number of records
            self.cursor.execute("SELECT COUNT(*) FROM messages;")
            record_count = self.cursor.fetchone()[0]

            # Get the number of unique authors
            self.cursor.execute("SELECT COUNT(DISTINCT author_name) FROM messages;")
            unique_authors = self.cursor.fetchone()[0]

            # Get the size of the database file
            db_size = os.path.getsize(self.database_file)

            # Format stats to fit on one line
            stats = (f'Records: {record_count}, Unique authors: {unique_authors}, '
                     f'DB size: {db_size} bytes')

            return stats

        except Error as e:
            print(e)

    def truncate_table(self, table_name):
        try:
            self.cursor.execute(f"DELETE FROM {table_name}")
            self.connection.commit()
            self.cursor.execute(f"VACUUM")
            print(f"Table {table_name} has been truncated. " + self.get_db_stats())
        except sqlite3.Error as e:
            print(f"An error occurred: {e.args[0]}")

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                role TEXT,
                author_name TEXT,
                content TEXT,
                assistant_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        self.connection.commit()

    def fetch_recent_messages(self, num_messages, author):
        self.cursor.execute(
            "SELECT author_name, content, assistant_response FROM messages WHERE author_name = ? ORDER BY timestamp ASC LIMIT ?",
            (author, num_messages)
        )
        return self.cursor.fetchall()

    def store_message(self, role, author_name, text, assistant_response=None):
        self.cursor.execute(
            "INSERT INTO messages (role, author_name, content, assistant_response) VALUES (?,?,?,?)",
            (role, author_name, text, assistant_response),
        )
        self.connection.commit()

    def delete_user_messages(self, author_name):
        try:
            self.cursor.execute("DELETE FROM messages WHERE author_name = ?", (author_name,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting messages from {author_name}: {e}")
            return False
