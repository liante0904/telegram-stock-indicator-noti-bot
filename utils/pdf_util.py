import pandas as pd
from fpdf import FPDF

# PDF 작성 함수
def create_pdf(filename, data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=5)
    pdf.add_page()

    # 나눔고딕 폰트 추가 (정상 폰트와 굵은 폰트 둘 다 등록)
    pdf.add_font('NanumGothic', '', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf', uni=True)
    pdf.add_font('NanumGothic-Bold', '', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf', uni=True)

    # 기본 폰트 설정
    # pdf.set_font('NanumGothic', size=16)

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

            # 사업 내용을 기본 스타일로 출력
            pdf.set_font('NanumGothic', size=16)
            pdf.multi_cell(0, 10, txt=f"사업내용: {item['Business Profile']}", align="L")
            pdf.ln(5)  # 줄 간격 추가

    pdf.output(filename)
    return filename
    