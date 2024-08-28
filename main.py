import os

import requests
from dotenv import load_dotenv
from flask import Flask
from flask_apscheduler import APScheduler

load_dotenv()

YOUR_API_KEY = os.getenv("YOUR_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))
PLAYER_UIDS = os.getenv("PLAYER_UID").split(",")
FIELDS_TO_MONITOR = ["isOnline", "isInGame"]


app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route("/")
def hello():
    return "哈囉 你們好 這裡是台灣 我是 台灣人阿扣 謝和弦"


@app.route("/healthz")
def healthz():
    return "I'm healthy❤️‍🩹", 200


@scheduler.task("cron", id="do_job", second=f"*/{CHECK_INTERVAL}")
def job():
    scheduled_task()


def scheduled_task():
    print("🔎 開始稽查")
    for player_uid in PLAYER_UIDS:
        check_api(player_uid)


last_values = {
    player_uid: {field_to_monitor: None for field_to_monitor in FIELDS_TO_MONITOR}
    for player_uid in PLAYER_UIDS
}


def check_api(player_uid):
    global last_values

    try:
        api_url = f"https://api.mozambiquehe.re/bridge?auth={YOUR_API_KEY}&uid={player_uid}&platform=PC"
        response = requests.get(api_url)
        data = response.json()

        for field_to_monitor in FIELDS_TO_MONITOR:
            current_value = data["realtime"][field_to_monitor]
            last_value = last_values[player_uid][field_to_monitor]

            if current_value != last_value:
                if last_value is not None:  # 避免第一次運行時觸發
                    content = None
                    player_name = data["global"]["name"]

                    if field_to_monitor == "isOnline":
                        emoji = ":partying_face:" if current_value else ":sleeping:"
                        status = "上線" if current_value else "離線"
                        content = f"{emoji} {player_name} 已{status}"

                    if field_to_monitor == "isInGame" and current_value:
                        selected_legend = data["realtime"]["selectedLegend"]
                        current_state_as_text = data["realtime"]["currentStateAsText"]

                        content = f":video_game: {player_name} playing {selected_legend} - {current_state_as_text}"

                    if content:
                        send_discord_notification(content)

                last_values[player_uid][field_to_monitor] = current_value

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")


def send_discord_notification(content):
    message = {"content": content}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        response.raise_for_status()
        print("✅ Discord 通知已發送")
    except requests.exceptions.RequestException as e:
        print(f"❌ 發送 Discord 通知時發生錯誤: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
