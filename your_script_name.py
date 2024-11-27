import requests
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# 文件路径，用于存储最后一次获取代币信息的时间
LAST_UPDATE_FILE = "last_update_time.json"

# 获取SOL链的最新代币资料
def get_sol_token_profiles() -> List[Dict[str, Any]]:
    """
    获取SOL链的最新代币资料

    Returns:
        list: SOL链的代币资料列表
    """
    url = "https://api.dexscreener.com/token-profiles/latest/v1"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()

        # 获取最后一次获取代币的时间
        last_update_time = get_last_update_time()

        # 筛选 chainId 为 solana 的代币，并检查更新时间
        sol_tokens = [
            token for token in data 
            if token.get("chainId") == "solana" and is_new_token(token, last_update_time)
        ]

        # 更新最后一次获取时间
        update_last_update_time()
        return sol_tokens
    except requests.RequestException as e:
        print(f"API请求错误: {e}")
        return []
    except ValueError as e:  # JSONDecodeError 是 ValueError 的子类
        print(f"JSON解析错误: {e}")
        return []

# 获取最后一次更新时间
def get_last_update_time() -> datetime:
    """
    获取上次更新的时间
    """
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data.get("last_update_time", "1970-01-01T00:00:00"))
    return datetime(1970, 1, 1)  # 默认返回一个非常早的时间

# 更新最后一次更新时间
def update_last_update_time() -> None:
    """
    更新最后一次更新时间
    """
    with open(LAST_UPDATE_FILE, 'w') as f:
        json.dump({"last_update_time": datetime.now().isoformat()}, f)

# 判断代币是否是新的
def is_new_token(token: Dict[str, Any], last_update_time: datetime) -> bool:
    """
    判断代币是否是新的（根据更新时间戳判断）

    Args:
        token (Dict[str, Any]): 代币资料
        last_update_time (datetime): 最后一次更新的时间

    Returns:
        bool: 如果代币是新的，返回True；否则返回False
    """
    token_time = datetime.fromisoformat(token.get("header", "1970-01-01T00:00:00"))
    return token_time > last_update_time

# 发送消息到 Telegram
def send_telegram_notification(tokens: List[Dict[str, Any]], bot_token: str, chat_id: str) -> None:
    """
    通过 Telegram 发送代币通知

    Args:
        tokens (List[Dict[str, Any]]): SOL链代币资料列表
        bot_token (str): Telegram Bot 的 Token
        chat_id (str): 接收消息的 Chat ID
    """
    if not tokens:
        message = "没有找到新的SOL链代币。"
        send_message_to_telegram(message, bot_token, chat_id)
        return

    message_parts = []
    current_message = ""
    for idx, token in enumerate(tokens, 1):
        token_info = f"代币 #{idx}\n{format_token_data(token)}\n{'-' * 40}\n"
        if len(current_message) + len(token_info) > 4000:
            message_parts.append(current_message)
            current_message = token_info
        else:
            current_message += token_info
    if current_message:
        message_parts.append(current_message)

    for part in message_parts:
        send_message_to_telegram(part, bot_token, chat_id)

# 发送单条消息到 Telegram
def send_message_to_telegram(message: str, bot_token: str, chat_id: str) -> None:
    """
    发送单条消息到 Telegram

    Args:
        message (str): 消息内容
        bot_token (str): Telegram Bot 的 Token
        chat_id (str): 接收消息的 Chat ID
    """
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message})
        response.raise_for_status()  # 检查请求是否成功
        print("Telegram消息已成功发送！")
    except requests.RequestException as e:
        print(f"Telegram消息发送失败: {e}")

# 主程序
def main():
    bot_token = "7520085438:AAFCG_Hzd5Fw_Rrp5Il4AnoR9MyvecI9pGg"
    chat_id = "6861809269"

    sol_tokens = get_sol_token_profiles()
    send_telegram_notification(sol_tokens, bot_token, chat_id)

if __name__ == "__main__":
    main()
