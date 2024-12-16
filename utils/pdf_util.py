import pandas as pd
from fpdf import FPDF
import requests
from io import BytesIO
import os
import tempfile
import warnings
import re

warnings.filterwarnings("ignore", message="cmap value too big/small")

from dotenv import load_dotenv

load_dotenv()
env = os.getenv('ENV')
font_dir = os.getenv('FONT_DIR')


def is_valid_ticker(ticker):
    """Ticker 유효성 검사 함수

    Args:
        ticker (str): 검사할 Ticker 문자열

    Returns:
        bool: 유효하면 True, 아니면 False
    """
    ticker_pattern = r'^[A-Z0-9-]+$'
    return re.match(ticker_pattern, ticker)

def download_image(url, filename):
    """이미지 다운로드 함수

    Args:
        url (str): 이미지 URL
        filename (str): 저장할 파일 이름

    Returns:
        str: 저장된 파일 경로 또는 에러 메시지
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        )
    }
    try:

        # User-Agent 헤더를 포함하여 요청
        # 리다이렉트를 따라가기 위해 allow_redirects=True 사용 (기본값이 True)
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생

        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    except requests.exceptions.RequestException as e:
        return f"이미지 다운로드 실패: {e}"
    except Exception as e:
        return f"기타 오류 발생: {e}"

def create_pdf(filename, data):
    """PDF 생성 함수

    Args:
        filename (str): 생성할 PDF 파일 이름
        data (DataFrame): 생성할 PDF에 사용할 데이터

    Returns:
        str: 생성된 PDF 파일 이름 또는 에러 메시지
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)
    pdf.add_page()

    # 나눔고딕 폰트 추가 (정상 폰트와 굵은 폰트 둘 다 등록)
    pdf.add_font('NanumGothic', '', f'{font_dir}/NanumGothic.ttf', uni=True)
    pdf.add_font('NanumGothic-Bold', '', f'{font_dir}/NanumGothicBold.ttf', uni=True)

    # 데이터가 그룹화된 상태일 경우
    for sector, group in data:
        pdf.set_text_color(0, 0, 0)
        
        # 각 섹터 제목을 굵은 폰트로 출력
        pdf.set_font('NanumGothic-Bold', size=18)
        pdf.cell(200, 10, txt=f"섹터: {sector}", ln=True)

        # 각 그룹 내의 항목들을 출력
        for _, item in group.iterrows():
            # 티커를 굵은 폰트로 출력
            pdf.set_font('NanumGothic-Bold', size=18)
            pdf.cell(200, 10, txt=f"티커: {item['Ticker']}", ln=True)

            pdf.ln(10)

            ticker = item['Ticker']
            if is_valid_ticker(ticker):
                img_url = f"https://finviz.com/chart.ashx?t={ticker}&ty=c&ta=1&p=d"
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                    img_path = download_image(img_url, temp_img.name)
                    if img_path.endswith('.png'):
                        pdf.image(img_path, x=10, y=None, w=100)
                    else:
                        pdf.set_font('NanumGothic', size=12)
                        pdf.cell(0, 10, txt=img_path, ln=True)

                os.remove(temp_img.name)
            else:
                pdf.set_font('NanumGothic', size=12)
                # pdf.cell(0, 10, txt=f"잘못된 Ticker 값: {ticker}", ln=True)

            pdf.ln(10)
            pdf.set_font('NanumGothic', size=16)
            pdf.multi_cell(0, 10, txt=f"사업내용: {item['Business Profile']}", align="L")

            pdf.ln(20)

    pdf.output(filename)
    return filename

if __name__ == '__main__':
    # 52주 신고가 종목 정보
    high_52_week_stocks = [
        {
            "Ticker": "XEL",
            "Sector": "Utilities",
            "Business Profile": "Xcel Energy Inc.는 자회사를 통해 세대, 구매, 전송, 유통 및 전기 판매에 참여합니다. 조절 된 전기 유틸리티"
        },
        {
            "Ticker": "AAPL",
            "Sector": "Technology",
            "Business Profile": "Apple Inc.는 혁신적인 전자제품, 소프트웨어 및 서비스의 설계, 제조 및 판매를 전문으로 합니다."
        },
        {
            "Ticker": "TSLA",
            "Sector": "Automotive",
            "Business Profile": "Tesla Inc.는 전기차 설계 및 제조와 에너지 저장 시스템 개발에 집중하는 회사입니다."
        }
    ]
    # 결과를 데이터프레임으로 정리
    high_52_week_df = pd.DataFrame(high_52_week_stocks, columns=['Ticker', 'Sector', 'Business Profile'])
    
    # 데이터프레임 출력
    print("전체 데이터프레임:")
    print(high_52_week_df)
    
    # 업종별로 그룹화
    grouped_by_sector = high_52_week_df.groupby('Sector')
    # 데이터프레임 출력
    print("52주 신고가 종목 데이터프레임:")
    create_pdf('test.pdf',grouped_by_sector)