import logging
import os

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從環境變數中取得設定
YOUR_API_KEY = os.getenv("YOUR_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))
PLAYER_UIDS = os.getenv("PLAYER_UID").split(",")
FIELDS_TO_MONITOR = ["isOnline", "isInGame"]

# 初始化上一次的值
last_values = {
    player_uid: {field_to_monitor: None for field_to_monitor in FIELDS_TO_MONITOR}
    for player_uid in PLAYER_UIDS
}


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# 檢查 API 並處理玩家狀態變化
def check_api(player_uid):
    global last_values

    try:
        # 呼叫 API 取得玩家資料
        api_url = f"https://api.mozambiquehe.re/bridge?auth={YOUR_API_KEY}&uid={player_uid}&platform=PC"
        response = requests.get(api_url)
        data = response.json()

        # 檢查監控的欄位
        for field_to_monitor in FIELDS_TO_MONITOR:
            current_value = data["realtime"][field_to_monitor]
            last_value = last_values[player_uid][field_to_monitor]

            # 如果值有變化，準備發送通知
            if current_value != last_value:
                if last_value is not None:  # 避免第一次執行時觸發
                    content = None
                    player_name = data["global"]["name"]
                    player_info = f"`UID:{player_uid}` **{player_name}**"

                    # 處理上線/離線狀態
                    if field_to_monitor == "isOnline":
                        emoji = ":partying_face:" if current_value else ":sleeping:"
                        status = "上線" if current_value else "離線"

                        content = f"{emoji} {player_info} 已{status}"

                    # 處理遊戲中狀態
                    if field_to_monitor == "isInGame" and current_value:
                        selected_legend = data["realtime"]["selectedLegend"]
                        current_state_as_text = data["realtime"]["currentStateAsText"]

                        content = f":video_game: {player_info} playing *{selected_legend}* - {current_state_as_text}"

                    # 發送 Discord 通知
                    if content:
                        send_discord_notification(content)

                # 更新上次的值
                last_values[player_uid][field_to_monitor] = current_value

    except Exception as e:
        logger.error(f"❌ 發生錯誤: {e}")


# 發送 Discord 通知
def send_discord_notification(content):
    message = {"content": content}

    try:
        # 發送 POST 請求到 Discord Webhook
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        response.raise_for_status()
        logger.info("✅ Discord 通知已發送")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 發送 Discord 通知時發生錯誤: {e}")


# 新增一個函數來執行所有玩家的檢查
def check_all_players():
    logger.info("🔎 開始稽查所有玩家")
    for player_uid in PLAYER_UIDS:
        check_api(player_uid)
    logger.info("✅ 完成本次稽查")


# 主程式進入點
if __name__ == "__main__":
    logger.info("🚀 程式啟動")

    # 創建一個 BlockingScheduler
    scheduler = BlockingScheduler()

    # 設定排程任務
    scheduler.add_job(
        check_all_players,
        trigger=CronTrigger(seconds="*/{CHECK_INTERVAL}"),
        id="check_players_job",
        name="檢查玩家狀態",
        replace_existing=True,
    )

    try:
        logger.info("⏰ 排程器已啟動")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("👋 程式已停止")
        scheduler.shutdown()
