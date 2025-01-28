import pandas as pd
import os
from telebot.callback_data import CallbackData
from pathlib import Path

user_path = Path("../project_yura/users.csv").resolve()

class UserCallbackData(CallbackData):
    max_streak = int
    words = dict
    word = str
    session_passes = int
    session_score = float
    session_correct = int
    session_answers = int
    session_streak = int



def read_users():
    return pd.read_csv(user_path)


def create_users(path):
    columns = ["user_id",
               "correct",
               "answers",
               "points",
               "max_streak",
               "passes"]
    users = pd.DataFrame(columns=columns)
    users.to_csv(path, index=False)


def save_changes(users):
    os.remove(user_path)
    users.to_csv(user_path, index=False)


def add_user(user_id):
    users = read_users()
    users = users._append({
        "user_id": user_id,
        "correct": 0,
        "answers": 0,
        "points": 0,
        "max_streak": 0,
        "passes": 0
    }, ignore_index=True)
    save_changes(users)
