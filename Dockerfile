# Python 3.10 베이스 이미지 사용
FROM python:3.10.12-slim

# 컨테이너의 작업 디렉토리 설정
WORKDIR /app

# 1. requirements.txt를 먼저 복사 (이 파일이 변경되지 않으면 이후 RUN 캐시 활용)
COPY requirements.txt requirements.txt

# 2. 의존성 파일을 먼저 설치
RUN pip install --no-cache-dir -r requirements.txt

# 3. 애플리케이션 파일 및 기타 리소스 복사
COPY main.py main.py
COPY .env .env
COPY modules/ modules/
COPY utils/ utils/


# 로컬 fonts 폴더를 Docker 컨테이너로 복사
COPY ./fonts /usr/share/fonts/

# 컨테이너에서 main 실행
CMD ["python", "main.py"]
