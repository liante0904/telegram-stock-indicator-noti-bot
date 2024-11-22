import requests
import yfinance as yf
import pandas as pd
from googletrans import Translator
import numpy as np
import asyncio
from tqdm import tqdm
import os
from dotenv import load_dotenv


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
        symbols = [stock["symbolCode"] for stock in stocks]
        print(f"총 {len(symbols)}개의 NASDAQ 100 종목을 가져왔습니다.")
        return symbols
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
    nasdaq100_tickers = get_nasdaq100_symbols_from_naver()
    if not nasdaq100_tickers:
        print("NASDAQ 100 목록을 가져오지 못했습니다.")
        return

    # 52주 신고가 종목을 저장할 리스트
    high_52_week_stocks = []

    print("52주 신고가 종목을 분석 중...")

    # tqdm를 명시적으로 관리
    with tqdm(total=len(nasdaq100_tickers), desc="Analyzing", unit="stock") as pbar:
        for idx, ticker in enumerate(nasdaq100_tickers):
            is_high = await find_52_week_high(ticker)
            pbar.update(1)  # 진행 상황 업데이트
            print(f"Analyzing {ticker} ({idx + 1} of {len(nasdaq100_tickers)})...")
            if not is_high:
                print(f"{ticker}: 52주 신고가 아님.")
                continue  # 52주 신고가가 아니면 건너뜀
            profile = await get_company_profile(ticker)
            high_52_week_stocks.append((ticker, profile['sector'], profile['description']))
            print(f"{ticker}: 52주 신고가 종목으로 추가됨.")

    if not high_52_week_stocks:
        print("\n52주 신고가 종목이 없습니다.")
    else:
        # 결과를 데이터프레임으로 정리
        high_52_week_df = pd.DataFrame(high_52_week_stocks, columns=['Ticker', 'Sector', 'Business Profile'])

        # 업종별로 그룹화하여 출력
        grouped_by_sector = high_52_week_df.groupby('Sector')

        print("\nNASDAQ 100 52주 신고가 종목 (업종별 분류 및 한글 번역된 사업내용 포함):")
        for sector, group in grouped_by_sector:
            print(f"\n업종: {sector}")
            for idx, row in group.iterrows():
                print(f"티커: {row['Ticker']}\n사업내용: {row['Business Profile']}\n")

# 메인 함수 실행
asyncio.run(analyze_nasdaq100())
