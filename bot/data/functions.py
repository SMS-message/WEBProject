import json
from typing import List, Dict


def log_all(message_chat_id: int):
    try:
        with open(f"logs/dialog_log_{message_chat_id}.json", mode="r", encoding="utf-8") as dialog_log:
            messages = json.load(dialog_log)
            try:
                with open(f"logs/log_{message_chat_id}.json", mode="r+", encoding="utf-8") as log_file:
                    log: List[List[Dict]] = json.load(log_file)
                    log.append(messages)
                with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8") as log_file:
                    pass
                with open(f"logs/log_{message_chat_id}.json", mode="r+", encoding="utf-8") as log_file:
                    json.dump(log, log_file, ensure_ascii=False, indent=2)
            except json.decoder.JSONDecodeError:
                with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8") as log_file:
                    json.dump([messages], log_file, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        with open(f"logs/log_{message_chat_id}.json", mode="w", encoding="utf-8") as log_file:
            json.dump([messages], log_file, ensure_ascii=False, indent=2)
    except Exception as err:
        print(f"У пользователя {message_chat_id} ошибка: {err}")


def log_dialog(history: List[Dict], message_chat_id: int):
    try:
        with open(f"logs/dialog_log_{message_chat_id}.json", mode="w", encoding="utf-8") as json_log:
            json.dump(history, json_log, ensure_ascii=False, indent=2)
    except Exception as err:
        print(f"У пользователя {message_chat_id} ошибка: {err}")
