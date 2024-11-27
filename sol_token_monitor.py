import requests
import json
import os
from typing import List

# 配置
BOT_TOKEN = "7520085438:AAFCG_Hzd5Fw_Rrp5Il4AnoR9MyvecI9pGg"
CHAT_ID = "6861809269"
SEEN_TOKENS_FILE = "seen_tokens.json"
API_URL = "https://api.dexscreener.com/token-profiles/latest/v1"

# 1. 加载已处理的代币地址
def load_seen_tokens() -> List[str]:
    """加载已记录的代币地址"""
    if os.path.exists(SEEN_TOKENS_FILE):
        with open(SEEN_TOKENS_FILE, "r") as f:
            return json.load(f)
    return []

# 2. 保存已处理的代币地址
def save_seen_tokens(seen_tokens: List[str]):
    """保存已记录的代币地址到文件"""
    with open(SEEN_TOKENS_FILE, "w") as f:
        json.dump(seen_tokens, f)

# 3. 获取最新的 SOL 链代币信息
def get_sol_token_profiles() -> List[dict]:
    """获取SOL链的最新代币资料"""
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API请求错误: {e}")
        return []

# 4. 筛选新代币
def filter_new_tokens(tokens: List[dict], seen_tokens: List[str]) -> List[dict]:
    """筛选出新代币"""
    new_tokens = []
    for token in tokens:
        if token.get("chainId") == "solana":
            token_address = token.get("tokenAddress")
            if token_address not in seen_tokens:
                new_tokens.append(token)
                seen_tokens.append(token_address)  # 更新记录
    return new_tokens

# 5. 发送 Telegram 通知
def send_telegram_notification(tokens: List[dict]):
    """通过 Telegram Bot 发送通知"""
    if not tokens:
        message = "未发现新的 SOL 链代币。"
    else:
        message = f"发现 {len(tokens)} 个新 SOL 链代币:\n\n"
        for idx, token in enumerate(tokens, 1):
            message += (
                f"代币 #{idx}\n"
                f"代币地址: {token.get('tokenAddress', 'N/A')}\n"
                f"描述: {token.get('description', '无描述')}\n"
                f"图标: {token.get('icon', 'N/A')}\n"
                f"DEX Screener链接: {token.get('url', 'N/A')}\n\n"
            )
            # 防止消息过长，分批发送
            if len(message) > 3500:  # Telegram 单条消息长度限制
                send_message_to_telegram(message)
                message = ""

    # 发送最后一段或完整消息
    if message:
        send_message_to_telegram(message)

def send_message_to_telegram(message: str):
    """发送消息到 Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram消息发送成功！")
    except requests.RequestException as e:
        print(f"Telegram消息发送失败: {e}")

# 6. 主函数
def main():
    print("正在获取最新 SOL 链代币信息...")
    all_tokens = get_sol_token_profiles()
    if not all_tokens:
        print("未能获取到代币信息。")
        return

    seen_tokens = load_seen_tokens()
    new_tokens = filter_new_tokens(all_tokens, seen_tokens)
    save_seen_tokens(seen_tokens)

    if new_tokens:
        print(f"发现 {len(new_tokens)} 个新代币，正在发送 Telegram 通知...")
    else:
        print("没有发现新代币。")

    send_telegram_notification(new_tokens)

# 启动程序
if __name__ == "__main__":
    main()
