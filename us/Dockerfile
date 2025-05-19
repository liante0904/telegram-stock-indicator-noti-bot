# Python 3.10 베이스 이미지 사용
FROM python:3.10.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt를 먼저 복사
COPY requirements.txt requirements.txt

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 코드 복사
COPY . .

# fonts 폴더 복사
COPY ./fonts /usr/share/fonts/

# 기본 명령 설정
CMD ["tail", "-f", "/dev/null"]
