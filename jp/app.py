import telegram
import time
import os
import asyncio

from nikkei_52wk import analyze_nikkei225
from topix_52wk import analyze_topix
from dotenv import load_dotenv

load_dotenv()
env = os.getenv('ENV')
token = os.getenv('TELEGRAM_BOT_TOKEN_REPORT_ALARM')
chat_id = os.getenv('TELEGRAM_CHANNEL_ID_STOCK_INDICATOR')

def sendMarkDownText(token, chat_id, sendMessageText=None, file=None, title=None, is_markdown=False):
    MAX_LENGTH = 4096  # Telegram 최대 메시지 길이
    bot = telegram.Bot(token=token)
    
    if sendMessageText is None and file is None:
        raise ValueError("Either 'sendMessageText' or 'file' must be provided")

    # 리스트 형태의 메시지 처리
    if isinstance(sendMessageText, list):
        total_parts = len(sendMessageText)
        for idx, message_chunk in enumerate(sendMessageText):
            final_message = f"**{title} (Part {idx + 1}/{total_parts})**\n\n" if title else ""
            final_message += message_chunk
            
            if is_markdown:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True, parse_mode='Markdown')
            else:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True)
            time.sleep(2)  # 메시지 전송 간 대기 시간 추가

    # 단일 문자열 메시지 처리
    elif isinstance(sendMessageText, str):
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

        messages = split_message(sendMessageText, MAX_LENGTH - (len(title) + 20 if title else 0))  # 여유분 확보
        total_parts = len(messages)
        for idx, message in enumerate(messages):
            final_message = f"**{title} (Part {idx + 1}/{total_parts})**\n\n" if title else ""
            final_message += message
            
            if is_markdown:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True, parse_mode='Markdown')
            else:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True)
            time.sleep(2)  # 동기적 호출이므로 대기 시간 추가

    # 파일 처리
    if file:
        if isinstance(file, str):  # 파일이 문자열이면 그냥 전송
            bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
        elif isinstance(file, list):  # 파일이 리스트면 순차적으로 전송
            for f in file:
                if isinstance(f, str):
                    bot.send_document(chat_id=chat_id, document=open(f, 'rb'))
                elif isinstance(f, dict) and 'file' in f:
                    bot.send_document(chat_id=chat_id, document=open(f['file'], 'rb'))
                time.sleep(2)  # 파일 전송 후 대기

async def main():
    # Analyze nikkei225
    high_52_week_stocks, nikkei225_pdf_file_name = await analyze_nikkei225()
    if high_52_week_stocks:
        sendMarkDownText(
            token=token,
            chat_id=chat_id,
            sendMessageText=high_52_week_stocks,  # 리스트 형태로 전달됨
            title="Nikkei225 52주 신고가 종목",
            is_markdown=True
        )
    
    # Analyze topix
    high_52_week_stocks, topix_pdf_file_name = await analyze_topix()
    if high_52_week_stocks:
        sendMarkDownText(
            token=token,
            chat_id=chat_id,
            sendMessageText=high_52_week_stocks,  # 리스트 형태로 전달됨
            title="TOPIX 52주 신고가 종목",
            is_markdown=True
        )

    # PDF 파일 전송
    if nikkei225_pdf_file_name:
        sendMarkDownText(
            token=token,
            chat_id=chat_id,
            file=nikkei225_pdf_file_name,
            title="Nikkei225 52주 신고가 PDF"
        )
    if topix_pdf_file_name:
        sendMarkDownText(
            token=token,
            chat_id=chat_id,
            file=topix_pdf_file_name,
            title="TOPIX 52주 신고가 PDF"
        )

if __name__ == "__main__":
    asyncio.run(main())