import requests
import yfinance as yf
import pandas as pd
from googletrans import Translator
import numpy as np
import asyncio
from tqdm import tqdm
import os
import sys
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

pdf_file_name = f"{now.strftime('%Y%m%d')[2:8]}_nikkei225_52wk_high.pdf"

# 현재 파일 기준으로 상위 디렉토리에 있는 .env 파일 경로 설정
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

# 현재 스크립트의 상위 디렉터리 경로를 추가
sys.path.append(base_dir)

from utils.pdf_util import create_pdf

# 환경 변수 사용
env = os.getenv('ENV')
naver_api_n225 = os.getenv('NAVER_API_NIKKEI225')

# Translator 객체 생성
translator = Translator()

# 네이버 API에서 nikkei225 종목 가져오기
def get_nikkei225_symbols_from_naver():
    url = naver_api_n225
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        data = response.json()
        stocks = data.get("stocks", [])
        symbols_with_names = [(f"{stock['symbolCode']}.T", stock['stockName']) for stock in stocks]  # (티커, 종목명) 쌍 생성
        print(f"총 {len(symbols_with_names)}개의 NIKKEI225 종목을 가져왔습니다.")
        return symbols_with_names
    except requests.RequestException as e:
        print(f"데이터를 가져오는 중 에러가 발생했습니다: {e}")
        return []

# 52주 신고가 종목 찾기
async def find_52_week_high(yf_ticker):
    try: 
        stock_data = yf.download(yf_ticker, period='1y', interval='1d', progress=False, auto_adjust=False)['Adj Close']
        if len(stock_data) == 0:
            return False  # 주가 데이터가 없는 경우 제외
        # 52주 최고가를 계산하고, 최근 주가가 52주 최고가와 같은지 확인
        highest_price_52_weeks = stock_data.max()
        current_price = stock_data.iloc[-1]
        return np.isclose(current_price, highest_price_52_weeks)  # 현재 가격과 최고가가 거의 동일하면 True
    except Exception:
        return False

# 회사의 사업내용 및 업종 가져오기
async def get_company_profile(yf_ticker):
    try:
        stock_info = yf.Ticker(yf_ticker).info
        description = stock_info.get('longBusinessSummary', 'No description available')
        # 사업내용을 한국어로 번역
        translated_description = translator.translate(description, src='en', dest='ko').text
        sector = stock_info.get('sector', 'No sector information')
        return {'description': translated_description, 'sector': sector}
    except Exception:
        return {'description': 'Error fetching or translating profile', 'sector': 'No sector information'}

# 메인 함수: nikkei225 종목 분석
async def analyze_nikkei225():
    print("nikkei225 종목 목록을 네이버 API에서 가져오는 중...")
    str_msg = ''
    nikkei225_tickers_with_names = get_nikkei225_symbols_from_naver()
    if not nikkei225_tickers_with_names:
        print("nikkei225 목록을 가져오지 못했습니다.")
        return

    # 52주 신고가 종목을 저장할 리스트
    high_52_week_stocks = []

    print("52주 신고가 종목을 분석 중...")

    # tqdm를 명시적으로 관리
    with tqdm(total=len(nikkei225_tickers_with_names), desc="Analyzing", unit="stock") as pbar:
        for idx, (ticker, name) in enumerate(nikkei225_tickers_with_names):
            is_high = await find_52_week_high(ticker)
            pbar.update(1)  # 진행 상황 업데이트
            print(f"Analyzing {ticker} ({idx + 1} of {len(nikkei225_tickers_with_names)})...")
            if not is_high:
                print(f"{ticker} ({name}): 52주 신고가 아님.")
                continue  # 52주 신고가가 아니면 건너뜀
            profile = await get_company_profile(ticker)
            high_52_week_stocks.append((ticker, name, profile['sector'], profile['description']))
            # profile['sector'] 기준으로 정렬
            high_52_week_stocks.sort(key=lambda x: x[1])  # sector(두 번째 요소) 기준으로 정렬
            print(f"{ticker}: 52주 신고가 종목으로 추가됨.")

    print('=' * 30)
    print("nikkei225 52주 신고가 종목 리스트")
    print('=' * 30)
    high_52_week_stocks_list = "nikkei225 52주 신고가 종목 리스트\n\n"

    if not high_52_week_stocks:
        high_52_week_stocks_list += "\n52주 신고가 종목이 없습니다."
        print(f"{high_52_week_stocks_list}")
    else:
        # 고정폭 글꼴을 사용한 표 형식
        header = f"{'티커':<10}{'종목명':<15}{'업종':<20}"
        separator = "-" * len(header)
        high_52_week_stocks_list += "```\n"  # 시작 부분에 줄바꿈 추가
        high_52_week_stocks_list += header + "\n"  # 헤더 뒤에 줄바꿈 추가
        high_52_week_stocks_list += separator + "\n"  # 구분선 뒤에 줄바꿈 추가

        for ticker, name, sector, description in high_52_week_stocks:
            high_52_week_stocks_list += f"{ticker:<10} {name:<15} {sector:<20}\n"  # 각 항목 뒤에 줄바꿈 추가

        high_52_week_stocks_list += "```"

        print(high_52_week_stocks_list)

    if not high_52_week_stocks:
        print("\n52주 신고가 종목이 없습니다.")
    else:
        # 결과를 데이터프레임으로 정리
        high_52_week_df = pd.DataFrame(high_52_week_stocks, columns=['Ticker', 'Name', 'Sector', 'Business Profile'])

        # 업종별로 그룹화하여 출력
        grouped_by_sector = high_52_week_df.groupby('Sector')
        for sector, group in grouped_by_sector:
            print(f"\n업종: {sector}")
            for idx, row in group.iterrows():
                print(f"티커: {row['Ticker']}\n종목명: {row['Name']}\n사업내용: {row['Business Profile']}")

        print("\nnikkei225 52주 신고가 종목 (업종별 분류 및 한글 번역된 사업내용 포함):")
        # PDF 생성
        send_pdf_file_name = ''
        if grouped_by_sector:
            send_pdf_file_name = create_pdf(pdf_file_name, grouped_by_sector)
        else:
            print(f"52주 신고가 데이터가 없거나 올바르지 않습니다. => {grouped_by_sector}")

    return high_52_week_stocks_list, send_pdf_file_name

if __name__ == '__main__':
    # 메인 함수 실행
    asyncio.run(analyze_nikkei225())
