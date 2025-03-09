import json
import os.path
import sqlite3
from typing import List, Dict, Tuple


def log_all(message_chat_id: int):
    try:
        with open(f"logs/dialog_log_{message_chat_id}.json", mode="r", encoding="utf-8") as dialog_log:
            messages = json.load(dialog_log)
            try:
                with open(f"logs/log_{message_chat_id}.json", mode="r+", encoding="utf-8") as log_file:
                    log: List[List[Dict]] = json.load(log_file)
                    log.append(messages)
                with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8"):
                    pass
                with open(f"logs/log_{message_chat_id}.json", mode="r+", encoding="utf-8") as log_file:
                    json.dump(log, log_file, ensure_ascii=False, indent=2)
            except json.decoder.JSONDecodeError:
                with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8") as log_file:
                    json.dump([messages], log_file, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        if os.path.exists(f"logs/log_{message_chat_id}.json"):
            with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8") as log_file:
                json.dump([messages], log_file, ensure_ascii=False, indent=2)
        else:
            with open(f"logs/dialog_log_{message_chat_id}.json", mode="w", encoding="utf-8"):
                pass
    except Exception as err:
        print(f"У пользователя {message_chat_id} ошибка: {err}")


def log_dialog(history: List[Dict], message_chat_id: int):
    try:
        with open(f"logs/dialog_log_{message_chat_id}.json", mode="w", encoding="utf-8") as json_log:
            json.dump(history, json_log, ensure_ascii=False, indent=2)
    except Exception as err:
        print(f"У пользователя {message_chat_id} ошибка: {err}")


def user_table_exists(user_id: int):
    con = sqlite3.connect("db/VideoHoster.db")
    cur = con.cursor()

    try:
        cur.execute(f"SELECT ID FROM User_{user_id}")
    except sqlite3.OperationalError as error:
        if "no such table" in error.args[0]:
            return False
    return True


def create_user_table(user_id: int):
    con = sqlite3.connect("db/VideoHoster.db")
    cur = con.cursor()

    cur.execute(f"""
                    CREATE TABLE User_{user_id} (
                        ID     INTEGER PRIMARY KEY,
                        viewed INTEGER DEFAULT (0) 
                    );
                    """)
    con.commit()

    cur.execute(f"""
                    INSERT INTO User_{user_id} (
                                          ID
                                      )
                                      SELECT ID
                                        FROM Videos;""")
    con.commit()


def make_queue(user_id: int) -> List[int]:
    con = sqlite3.connect("db/VideoHoster.db")
    cur = con.cursor()

    res = tuple(cur.execute(f"""SELECT ID
                          FROM User_{user_id}
                         WHERE viewed = 0;"""))
    if res:
        return refactor_result(res)
    res = tuple(cur.execute(f"""SELECT ID
                                  FROM User_{user_id}
                                 WHERE ID IN (
                                           SELECT ID
                                             FROM Videos
                                            WHERE dislikes == 0
                                       );
                                """))
    if res:
        return refactor_result(res)

    res = tuple(cur.execute(f"""SELECT ID
                                  FROM User_{user_id}
                                 WHERE ID IN (
                                           SELECT ID
                                             FROM Videos
                                            WHERE likes >= dislikes
                                       );
                                    """))
    if res:
        return refactor_result(res)

    res = tuple(cur.execute(f"""SELECT ID
                                      FROM User_{user_id}"""))
    return refactor_result(res)


def update_user_table(user_id: int):
    con = sqlite3.connect("db/VideoHoster.db")
    cur = con.cursor()

    cur.execute(f"""
                    INSERT INTO User_{user_id} (
                               ID
                           )
                           SELECT ID
                             FROM Videos
                            WHERE ID NOT IN (
                                      SELECT ID
                                        FROM User_{user_id}
                                  );
                    """)
    con.commit()


def refactor_result(res: Tuple[Tuple[int]]) -> List[int]:
    result = []
    for elem in res:
        result.append(elem[0])

    return result
