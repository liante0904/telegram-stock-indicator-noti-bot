import pandas as pd
from fpdf import FPDF
import requests
from io import BytesIO
import os
import tempfile
import warnings
warnings.filterwarnings("ignore", message="cmap value too big/small")

from dotenv import load_dotenv

load_dotenv()
env = os.getenv('ENV')
font_dir = os.getenv('FONT_DIR')

# PDF 작성 함수
def create_pdf(filename, data):
    print(data)
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

            # 이미지 삽입
            pdf.ln(10)  # 줄 간격 추가
            try:
                # 이미지 URL 설정
                img_url = f"https://finviz.com/chart.ashx?t={item['Ticker']}&ty=c&ta=1&p=d"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15'
                }
                
                # 이미지 다운로드
                response = requests.get(img_url, headers=headers)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    
                    # 임시 파일 생성
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                        temp_img.write(img_data.getvalue())
                        temp_img_path = temp_img.name

                    # 이미지 삽입
                    pdf.image(temp_img_path, x=10, y=None, w=100)

                    # 임시 파일 삭제
                    os.remove(temp_img_path)
                else:
                    pdf.set_font('NanumGothic', size=12)
                    pdf.cell(0, 10, txt="이미지를 불러오는 데 실패했습니다.", ln=True)
            except Exception as e:
                pdf.set_font('NanumGothic', size=12)
                pdf.cell(0, 10, txt=f"이미지 삽입 중 오류 발생: {e}", ln=True)
                
            pdf.ln(10)  # 줄 간격 추가
            
            # 사업 내용을 기본 스타일로 출력
            pdf.set_font('NanumGothic', size=16)
            pdf.multi_cell(0, 10, txt=f"사업내용: {item['Business Profile']}", align="L")
            

            pdf.ln(20)  # 다음 아이템과의 간격 추가

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