import sqlite3
import os
from flask_login import UserMixin

class ForumDatabase:
    def __init__(self, dbname):
        self.dbname = dbname
        self.dbpath = f'{os.path.split(__file__)[0]}\data'
        
        if os.path.exists(f'{self.dbpath}\{self.dbname}.db'):
            self.connection = sqlite3.connect(f'{self.dbpath}\{self.dbname}.db', check_same_thread=False)
            self.cursor = self.connection.cursor() 
        else:
            self.connection = sqlite3.connect(f'{self.dbpath}\{self.dbname}.db')
            self.cursor = self.connection.cursor()
            self.create_tables()
 
    def create_tables(self):
        self.cursor.executescript("""CREATE TABLE users(
                                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT,
                                        avatar_url TEXT,
                                        login TEXT,
                                        password TEXT);
                            
                                    CREATE TABLE threads(
                                        thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id INTEGER,
                                        thread_subject TEXT,
                                        thread_posts INTEGER,
                                        thread_last_time TEXT);

                                    CREATE TABLE posts(
                                        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        user_id INTEGER,
                                        thread_id INTEGER,
                                        post_text TEXT,
                                        post_time TEXT)""")
        
class User(UserMixin):
    def __init__(self, user_id, name, avatar_url, login, password):
        self.user_id = user_id
        self.name = name
        self.avatar_url = avatar_url
        self.login = login
        self.password = password 

    def get_id(self):
        return self.user_id


