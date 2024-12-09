# Python 3.10 베이스 이미지 사용
FROM python:3.10.12-slim

# 컨테이너의 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt requirements.txt

# Flask 앱 파일 복사
COPY main.py main.py
COPY .env .env
COPY modules/ modules/  
COPY utils/ utils/  


# 로컬 fonts 폴더를 Docker 컨테이너로 복사
COPY ./fonts /usr/share/fonts/

RUN  pip install --no-cache-dir -r requirements.txt 

# 컨테이너에서 main 실행
CMD ["python", "main.py"]
