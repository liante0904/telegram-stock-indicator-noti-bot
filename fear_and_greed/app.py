import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import telegram

# .env 파일 로드
load_dotenv()
env = os.getenv('ENV')
token = os.getenv('TELEGRAM_BOT_TOKEN_REPORT_ALARM')
chat_id = os.getenv('TELEGRAM_CHANNEL_ID_STOCK_INDICATOR')
cnn_url = os.getenv('CNN_FEAR_AND_GREED_URL')

print(token, chat_id, cnn_url)

async def sendMarkDownText(token, chat_id, sendMessageText=None, file=None, title=None, is_markdown=False):
    MAX_LENGTH = 3000  # 메시지 최대 길이
    bot = telegram.Bot(token=token)

    if sendMessageText is None and file is None:
        raise ValueError("Either 'sendMessageText' or 'file' must be provided")

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
        messages = split_message(sendMessageText, MAX_LENGTH - (len(title) + 11 if title else 0))

        for idx, message in enumerate(messages):
            final_message = ""
            if title:
                final_message += f"타이틀: {title}\n\n"
            final_message += message

            if is_markdown:
                await bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True, parse_mode='Markdown')
            else:
                await bot.send_message(chat_id=chat_id, text=final_message, disable_web_page_preview=True)

            await asyncio.sleep(2)  # 동기적 호출이므로 대기 시간 추가

    elif file:
        if isinstance(file, str):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                await bot.send_photo(chat_id=chat_id, photo=open(file, 'rb'), caption=title if title else None)
            else:
                await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
        elif isinstance(file, list):
            for f in file:
                if isinstance(f, str):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        await bot.send_photo(chat_id=chat_id, photo=open(f, 'rb'), caption=title if title else None)
                    else:
                        await bot.send_document(chat_id=chat_id, document=open(f, 'rb'))
                elif isinstance(f, dict) and 'file' in f:
                    if f['file'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        await bot.send_photo(chat_id=chat_id, photo=open(f['file'], 'rb'), caption=f.get('title', None))
                    else:
                        await bot.send_document(chat_id=chat_id, document=open(f['file'], 'rb'))
                await asyncio.sleep(2)  # 파일 전송 후 대기
    else:
        print('확인필요')

async def main():
    # 날짜 기반 파일명 생성
    today_date = datetime.now().strftime("%y%m%d")
    output_filename = f"{today_date}_fear-and-greed.png"
    output_filename_sent = f"{today_date}_fear-and-greed_send.png"

    # 파일 존재 여부 확인
    if os.path.exists(output_filename_sent):
        print(f"{output_filename_sent} already exists. Exiting program.")
        return

    if os.path.exists(output_filename):
        print(f"{output_filename} exists but not sent. Proceeding to send.")
    else:
        print(f"{output_filename} does not exist. Creating a new file.")

    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 필요 시 활성화
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        # command_executor="http://localhost:4444/wd/hub",
        command_executor="http://selenium:4444/wd/hub",  # Docker 내부에서 실행 시
        options=chrome_options
    )

    driver.set_window_size(390, 844)  # iPhone 13 Pro 논리적 해상도

    try:
        # CNN Fear and Greed 페이지 접속
        driver.get(cnn_url or "https://edition.cnn.com/markets/fear-and-greed")
        time.sleep(3)

        # 특정 영역으로 스크롤
        target_element = driver.find_element(By.XPATH, "/html/body/div[1]/section[4]/section[1]/section[1]/div/section/div[1]/div[2]/div[1]/div/div[1]")
        driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
        time.sleep(1)

        # 요소가 화면 중앙에 오도록 추가 스크롤 조정
        driver.execute_script("window.scrollBy(0, -200);")  # 위로 150px 스크롤
        time.sleep(1)

        viewport_screenshot_path = "temp_viewport_screenshot.png"
        driver.save_screenshot(viewport_screenshot_path)
        print(f"Viewport screenshot saved at {viewport_screenshot_path}")

        # 스크롤바 너비 계산
        scrollbar_width = driver.execute_script("""
            return window.innerWidth - document.documentElement.clientWidth;
        """)
        print(f"Scrollbar width: {scrollbar_width}px")

        # 이미지 크기 조정 (스크롤바 제외)
        with Image.open(viewport_screenshot_path) as img:
            width, height = img.size
            print(f"Original image size: {width}x{height}")

            # 오른쪽 스크롤바 영역 제외한 크롭
            cropped_img = img.crop((0, 0, width - scrollbar_width, height))
            cropped_img.save(output_filename)

        print(f"Final screenshot saved at {output_filename}")

        if os.path.exists(viewport_screenshot_path):
            os.remove(viewport_screenshot_path)
            print(f"Temporary file {viewport_screenshot_path} deleted.")

        await sendMarkDownText(token, chat_id, file=output_filename)

        os.rename(output_filename, output_filename_sent)
        print(f"File renamed to {output_filename_sent}")

    finally:
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())
