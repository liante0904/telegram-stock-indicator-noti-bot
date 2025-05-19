# Python 3.10 베이스 이미지 사용
FROM python:3.10.12-slim

# 필수 패키지 설치 (curl, unzip 등)
RUN apt-get update && apt-get install -y curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# uv 경로 추가
ENV PATH="/root/.cargo/bin:$PATH"

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사
COPY requirements.txt requirements.txt

# 의존성 설치 (uv pip 사용)
RUN pip install uv

# uv 경로 직접 지정해서 설치
RUN /root/.cargo/bin/uv pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 폰트 복사
COPY ./fonts /usr/share/fonts/

# 기본 명령 설정 (필요에 따라 수정 가능)
CMD ["tail", "-f", "/dev/null"]
