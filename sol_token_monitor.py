import requests
import json
import os
from typing import List, Dict

# Telegram 配置
BOT_TOKEN = "7520085438:AAFCG_Hzd5Fw_Rrp5Il4AnoR9MyvecI9pGg"
CHAT_ID = "6861809269"

# API 配置
API_URL = "https://api.dexscreener.com/token-profiles/latest/v1"
CHAIN_ID = "solana"
SEEN_TOKENS_FILE = "seen_tokens.json"

def send_telegram_message(message: str):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("Telegram 消息已成功发送！")
    except requests.exceptions.RequestException as e:
        print(f"Telegram 消息发送失败: {e}")

def load_seen_tokens() -> set:
    """加载已记录的代币地址"""
    if os.path.exists(SEEN_TOKENS_FILE):
        with open(SEEN_TOKENS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_tokens(seen_tokens: set):
    """保存已记录的代币地址"""
    with open(SEEN_TOKENS_FILE, "w") as f:
        json.dump(list(seen_tokens), f)

def fetch_latest_tokens() -> List[Dict]:
    """获取最新代币信息"""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        tokens = response.json()
        return tokens if isinstance(tokens, list) else []
    except requests.exceptions.RequestException as e:
        print(f"无法获取最新代币信息: {e}")
        return []

def format_token_message(token: Dict) -> str:
    """格式化单个代币信息为 Telegram 消息"""
    url = token.get("url", "N/A")
    chain_id = token.get("chainId", "N/A")
    token_address = token.get("tokenAddress", "N/A")
    icon = token.get("icon", "N/A")
    header = token.get("header", "N/A")
    description = token.get("description", "N/A")
    links = token.get("links", [])
    
    # 格式化相关链接
    formatted_links = "\n".join(
        [f"- {link.get('label', 'N/A')}: <a href='{link.get('url', '#')}'>Link</a>" for link in links]
    )
    
    return (
        f"<b>代币页面:</b> <a href='{url}'>{url}</a>\n"
        f"<b>链标识:</b> {chain_id}\n"
        f"<b>代币地址:</b> {token_address}\n"
        f"<b>图标:</b> <a href='{icon}'>{icon}</a>\n"
        f"<b>头图:</b> <a href='{header}'>{header}</a>\n"
        f"<b>描述:</b> {description}\n"
        f"<b>相关链接:</b>\n{formatted_links if formatted_links else 'N/A'}"
    )

def main():
    # 加载已记录的代币
    seen_tokens = load_seen_tokens()

    # 获取最新代币信息
    latest_tokens = fetch_latest_tokens()
    if not latest_tokens:
        send_telegram_message("未找到最新代币信息。")
        return

    # 过滤出新代币
    new_tokens = [token for token in latest_tokens if token["tokenAddress"] not in seen_tokens]
    if not new_tokens:
        send_telegram_message("没有找到新的 SOL 链代币。")
        return

    # 发送每个新代币的消息
    for token in new_tokens:
        if token["chainId"] == CHAIN_ID:  # 确保链标识为 Solana
            message = format_token_message(token)
            send_telegram_message(message)
            seen_tokens.add(token["tokenAddress"])

    # 保存更新的代币地址
    save_seen_tokens(seen_tokens)

if __name__ == "__main__":
    main()
