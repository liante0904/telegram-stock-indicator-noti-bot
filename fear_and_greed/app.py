from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Remote(
    command_executor="http://selenium:4444/wd/hub",
    options=chrome_options
)

driver.set_window_size(390, 844)  # iPhone 13 Pro 논리적 해상도

try:
    # CNN Fear and Greed 페이지 접속
    driver.get("https://edition.cnn.com/markets/fear-and-greed")
    time.sleep(3)

    # 특정 영역으로 스크롤
    target_element = driver.find_element(By.XPATH, "/html/body/div[1]/section[4]/section[1]/section[1]/div/section/div[1]/div[2]/div[1]/div/div[1]")
    driver.execute_script("arguments[0].scrollIntoView(true);", target_element)
    time.sleep(1)

    # 요소가 화면 중앙에 오도록 추가 스크롤 조정
    driver.execute_script("window.scrollBy(0, -200);")  # 위로 150px 스크롤
    time.sleep(1)

    # 화면에 보이는 영역만 스크린샷
    viewport_screenshot_path = "viewport_screenshot.png"
    driver.save_screenshot(viewport_screenshot_path)
    print(f"Viewport screenshot saved at {viewport_screenshot_path}")

    # 스크롤바 너비 계산
    scrollbar_width = driver.execute_script("""
        return window.innerWidth - document.documentElement.clientWidth;
    """)
    print(f"Scrollbar width: {scrollbar_width}px")

    # 이미지 크기 조정 (스크롤바 제외)
    cropped_screenshot_path = "cropped_screenshot.png"
    with Image.open(viewport_screenshot_path) as img:
        width, height = img.size
        print(f"Original image size: {width}x{height}")

        # 오른쪽 스크롤바 영역 제외한 크롭
        cropped_img = img.crop((0, 0, width - scrollbar_width, height))
        cropped_img.save(cropped_screenshot_path)

    print(f"Cropped screenshot saved at {cropped_screenshot_path}")
finally:
    driver.quit()
