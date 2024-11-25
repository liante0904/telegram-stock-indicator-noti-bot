import telegram
import time
import os
import asyncio


from modules.nasdaq_52wk import analyze_nasdaq100
from modules.snp_52wk import analyze_sp500

# from utils.telegram_util import sendMarkDownText

from dotenv import load_dotenv

load_dotenv()
env = os.getenv('ENV')
token = os.getenv('TELEGRAM_BOT_TOKEN_REPORT_ALARM')
chat_id = os.getenv('TELEGRAM_CHANNEL_ID_STOCK_INDICATOR')

async def main():
    
    # Analyze NASDAQ and SP500
    sendMessageText = await analyze_nasdaq100()
    print(sendMessageText)
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        sendMessageText=sendMessageText
    )
    
    sendMessageText = await analyze_sp500()
    print(sendMessageText)
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        sendMessageText=sendMessageText
    )

def sendMarkDownText(token, chat_id, sendMessageText, title=None):
    MAX_LENGTH = 3000  # 메시지 최대 길이
    bot = telegram.Bot(token=token)

    # 메시지를 '\n' 기준으로 분리하여 3000자 이하로 분리
    def split_message(text, max_length):
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 <= max_length:
                current_chunk += line + '\n'
            else:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    # 메시지를 분리
    messages = split_message(sendMessageText, MAX_LENGTH - (len(title) + 11 if title else 0))
    
    # 분리된 메시지를 순차적으로 발송
    for idx, message in enumerate(messages):
        final_message = ""
        if title:
            final_message += f"타이틀: {title}\n\n"
        final_message += message
        
        # 메시지 발송
        bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True)
        time.sleep(2)  # 동기적 호출이므로 대기 시간 추가
        
if __name__ == "__main__":
    asyncio.run(main())
