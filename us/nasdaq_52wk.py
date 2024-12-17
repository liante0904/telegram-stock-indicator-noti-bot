import requests
import yfinance as yf
import pandas as pd
from googletrans import Translator
import numpy as np
import asyncio
import sys
from tqdm import tqdm
import os
from dotenv import load_dotenv
from datetime import datetime

now = datetime.now()

print("현재 : ", now)
print("현재 날짜 : ", now.date())
print("현재 시간 : ", now.time())
print("timestamp : ", now.timestamp())
print("년 : ", now.year)
print("월 : ", now.month)
print("일 : ", now.day)
print("시 : ", now.hour)
print("분 : ", now.minute)
print("초 : ", now.second)
print("마이크로초 : ", now.microsecond)
print("요일 : ", now.weekday())
print("문자열 변환 : ", now.strftime('%Y%m%d')[2:8])

pdf_file_name = f"{now.strftime('%Y%m%d')[2:8]}_nsd100_52wk_high.pdf"

# 현재 파일 기준으로 상위 디렉토리에 있는 .env 파일 경로 설정
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# 현재 스크립트의 상위 디렉터리 경로를 추가
sys.path.append(base_dir)

from utils.pdf_util import create_pdf

# 현재 파일 기준으로 상위 디렉토리에 있는 .env 파일 경로 설정
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# 환경 변수 사용
env = os.getenv('ENV')
naver_api_snp = os.getenv('NAVER_API_NQ100')

# Translator 객체 생성
translator = Translator()

# 네이버 API에서 NASDAQ 100 종목 가져오기
def get_nasdaq100_symbols_from_naver():
    url = naver_api_snp
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        data = response.json()
        stocks = data.get("stocks", [])
        print(f"총 {len(stocks)}개의 NASDAQ 100 종목을 가져왔습니다.")
        
        symbols_with_names = [(stock["symbolCode"], stock["stockName"]) for stock in stocks]
        return symbols_with_names
    except requests.RequestException as e:
        print(f"데이터를 가져오는 중 에러가 발생했습니다: {e}")
        return []

# 52주 신고가 종목 찾기
async def find_52_week_high(ticker):
    try:
        # 티커에 '.'가 있으면 '-'로 변환
        yf_ticker = ticker.replace('.', '-')
        stock_data = yf.download(yf_ticker, period='1y', interval='1d', progress=False)['Adj Close']
        if len(stock_data) == 0:
            return False  # 주가 데이터가 없는 경우 제외
        # 52주 최고가를 계산하고, 최근 주가가 52주 최고가와 같은지 확인
        highest_price_52_weeks = stock_data.max()
        current_price = stock_data.iloc[-1]
        return np.isclose(current_price, highest_price_52_weeks)  # 현재 가격과 최고가가 거의 동일하면 True
    except Exception:
        return False

# 회사의 사업내용 및 업종 가져오기
async def get_company_profile(ticker):
    try:
        # 티커에 '.'가 있으면 '-'로 변환
        yf_ticker = ticker.replace('.', '-')
        stock_info = yf.Ticker(yf_ticker).info
        description = stock_info.get('longBusinessSummary', 'No description available')
        # 사업내용을 한국어로 번역
        translated_description = translator.translate(description, src='en', dest='ko').text
        sector = stock_info.get('sector', 'No sector information')
        return {'description': translated_description, 'sector': sector}
    except Exception:
        return {'description': 'Error fetching or translating profile', 'sector': 'No sector information'}

# 메인 함수: NASDAQ 100 종목 분석
async def analyze_nasdaq100():
    print("NASDAQ 100 종목 목록을 네이버 API에서 가져오는 중...")
    nasdaq100_tickers_with_names = get_nasdaq100_symbols_from_naver()
    if not nasdaq100_tickers_with_names:
        print("NASDAQ 100 목록을 가져오지 못했습니다.")
        return

    # 52주 신고가 종목을 저장할 리스트
    high_52_week_stocks = []

    print("52주 신고가 종목을 분석 중...")

    # tqdm를 명시적으로 관리
    with tqdm(total=len(nasdaq100_tickers_with_names), desc="Analyzing", unit="stock") as pbar:
        for idx, (ticker, name) in enumerate(nasdaq100_tickers_with_names):
            is_high = await find_52_week_high(ticker)
            pbar.update(1)  # 진행 상황 업데이트
            print(f"Analyzing {ticker} ({idx + 1} of {len(nasdaq100_tickers_with_names)})...")
            
            if not is_high:
                print(f"{name} ({ticker}): 52주 신고가 아님.")
                continue  # 52주 신고가가 아니면 건너뜀
            
            profile = await get_company_profile(ticker)
            high_52_week_stocks.append((ticker, name, profile['sector'], profile['description']))
            print(f"{name} ({ticker}): 52주 신고가 종목으로 추가됨.")

    print('=' * 40)
    print("NASDAQ 100 52주 신고가 종목 리스트")
    print('=' * 40)

    high_52_week_stocks_list = "NASDAQ 100 52주 신고가 종목 리스트\n\n"
    
    if not high_52_week_stocks:
        high_52_week_stocks_list += "\n52주 신고가 종목이 없습니다."
        print(f"{high_52_week_stocks_list}")
    else:
        # 고정폭 글꼴을 사용한 표 형식
        header = f"{'티커':<10}{'종목명':<20}{'업종':<20}"
        separator = "-" * len(header)
        high_52_week_stocks_list += "```\n"
        high_52_week_stocks_list += header + "\n"
        high_52_week_stocks_list += separator + "\n"

        for ticker, name, sector, description in high_52_week_stocks:
            high_52_week_stocks_list += f"{ticker:<10}{name:<20}{sector:<20}\n"

        high_52_week_stocks_list += "```"

        print(high_52_week_stocks_list)

    if not high_52_week_stocks:
        print("\n52주 신고가 종목이 없습니다.")
    else:
        # 결과를 데이터프레임으로 정리
        high_52_week_df = pd.DataFrame(high_52_week_stocks, columns=['Ticker', 'Name', 'Sector', 'Business Profile'])

        # 업종별로 그룹화하여 PDF 생성
        grouped_by_sector = high_52_week_df.groupby('Sector')
        send_pdf_file_name = create_pdf(pdf_file_name, grouped_by_sector)

        print(f"\nPDF 파일이 생성되었습니다: {send_pdf_file_name}")

    return high_52_week_stocks_list, send_pdf_file_name


if __name__ == '__main__':
    # 메인 함수 실행
    asyncio.run(analyze_nasdaq100())
