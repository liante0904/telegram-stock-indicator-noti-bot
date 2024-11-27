import telegram
import time
import os
import asyncio

from modules.nasdaq_52wk import analyze_nasdaq100
from modules.snp_52wk import analyze_sp500

from dotenv import load_dotenv

load_dotenv()
env = os.getenv('ENV')
token = os.getenv('TELEGRAM_BOT_TOKEN_REPORT_ALARM')
chat_id = os.getenv('TELEGRAM_CHANNEL_ID_STOCK_INDICATOR')


def sendMarkDownText(token, chat_id, sendMessageText=None, file=None,title=None, is_markdown=False):
    MAX_LENGTH = 3000  # 메시지 최대 길이
    bot = telegram.Bot(token=token)
    
    if sendMessageText is None and file is None:
        raise ValueError("Either 'sendMessageText' or 'file' must be provided")

    # 메시지를 '\n' 기준으로 분리하여 3000자 이하로 분리
    def split_message(text, max_length):
        lines = text.split('\n\n')
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

    if sendMessageText:
        # 메시지를 분리
        messages = split_message(sendMessageText, MAX_LENGTH - (len(title) + 11 if title else 0))
        
        # 분리된 메시지를 순차적으로 발송
        for idx, message in enumerate(messages):
            final_message = ""
            if title:
                final_message += f"타이틀: {title}\n\n"
            final_message += message
            
            # 메시지 발송
            if is_markdown:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True, parse_mode='Markdown')
            # 파일 처리
            elif file:
                if isinstance(file, str):  # 파일이 문자열이면 그냥 전송
                    bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
                elif isinstance(file, list):  # 파일이 리스트나 딕셔너리 형식이면 순차적으로 전송
                    for f in file:
                        if isinstance(f, str):  # 파일 경로가 문자열인 경우
                            bot.send_document(chat_id=chat_id, document=open(f, 'rb'))
                        elif isinstance(f, dict) and 'file' in f:  # 딕셔너리인 경우 'file' 키를 찾아서 처리
                            bot.send_document(chat_id=chat_id, document=open(f['file'], 'rb'))
                        time.sleep(2)  # 파일 전송 후 대기
            else:
                bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True)
            
            time.sleep(2)  # 동기적 호출이므로 대기 시간 추가
    elif file:
        if isinstance(file, str):  # 파일이 문자열이면 그냥 전송
            bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
        elif isinstance(file, list):  # 파일이 리스트나 딕셔너리 형식이면 순차적으로 전송
            for f in file:
                if isinstance(f, str):  # 파일 경로가 문자열인 경우
                    bot.send_document(chat_id=chat_id, document=open(f, 'rb'))
                elif isinstance(f, dict) and 'file' in f:  # 딕셔너리인 경우 'file' 키를 찾아서 처리
                    bot.send_document(chat_id=chat_id, document=open(f['file'], 'rb'))
                    
                time.sleep(2)  # 파일 전송 후 대기
    else:
        print('확인필요')
        
async def main():
    # Analyze NASDAQ and SP500
    high_52_week_stocks, nsd100_pdf_file_name = await analyze_nasdaq100()
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        sendMessageText=high_52_week_stocks,
        is_markdown=True  # Markdown을 사용할 때는 True로 설정
    )
    
    high_52_week_stocks, snp500_pdf_file_name = await analyze_sp500()
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        sendMessageText=high_52_week_stocks,
        is_markdown=True  # Markdown을 사용할 때는 True로 설정
    )

    # pdf 전송
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        file=nsd100_pdf_file_name
    )
    sendMarkDownText(
        token=token,
        chat_id=chat_id,
        file=snp500_pdf_file_name
    )

    

if __name__ == "__main__":
    asyncio.run(main())