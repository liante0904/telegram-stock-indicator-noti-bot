FROM python:3.10.12-slim

# 필요한 패키지 설치
RUN pip install --no-cache-dir selenium pillow

# 애플리케이션 코드 복사
COPY app.py /app/app.py

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 실행
CMD ["python", "app.py"]