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
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        sendMessageText="test111"
    )
    
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
# 가공없이 텍스트를 발송합니다. (동기적 방식)
def sendMarkDownText(token, chat_id, sendMessageText): 
    time.sleep(1)  # time.sleep()은 동기적 호출이므로 await 사용 불필요
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=sendMessageText, disable_web_page_preview=True)

if __name__ == "__main__":
    asyncio.run(main())
