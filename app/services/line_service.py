import requests
from app.config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USERS_FILE
from app.services.json_service import load_json, save_json


def save_line_user(user_id: str):
    users = load_json(LINE_USERS_FILE, [])

    if user_id not in users:
        users.append(user_id)
        save_json(LINE_USERS_FILE, users)


def send_line_message(message: str):
    users = load_json(LINE_USERS_FILE, [])

    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
        return

    if not users:
        print("通知先LINEユーザーが登録されていません")
        return

    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }

    for user_id in users:
        payload = {
            "to": user_id,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code >= 300:
            print("LINE送信エラー:", response.status_code, response.text)