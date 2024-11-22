#!/bin/bash

# 사용자 설정 변수
PYTHON_VERSION="3.10.12"  # 사용할 Python 버전
VIRTUAL_ENV_NAME="pyenv-indicator"   # 생성할 버추얼 환경 이름
TARGET_FOLDER="/root/dev/telegram-indicator-noti-bot"  # 자동 활성화할 폴더 경로 설정

# pyenv 설치 확인
if ! command -v pyenv &> /dev/null; then
    echo "pyenv가 설치되어 있지 않습니다. 먼저 pyenv를 설치하세요."
    exit 1
fi

# Python 버전 설치 (이미 설치되어 있다면 스킵)
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Python $PYTHON_VERSION 설치 중..."
    pyenv install $PYTHON_VERSION
else
    echo "Python $PYTHON_VERSION 이미 설치됨."
fi

# 버추얼 환경 생성 (이미 존재하면 스킵)
if ! pyenv versions | grep -q "$VIRTUAL_ENV_NAME"; then
    echo "버추얼 환경 '$VIRTUAL_ENV_NAME' 생성 중..."
    pyenv virtualenv $PYTHON_VERSION $VIRTUAL_ENV_NAME
else
    echo "버추얼 환경 '$VIRTUAL_ENV_NAME' 이미 존재함."
fi

# 대상 폴더 생성 (존재하지 않으면 생성)
if [ ! -d "$TARGET_FOLDER" ]; then
    echo "폴더 '$TARGET_FOLDER' 생성 중..."
    mkdir -p $TARGET_FOLDER
else
    echo "폴더 '$TARGET_FOLDER' 이미 존재함."
fi

# 해당 폴더로 이동
cd $TARGET_FOLDER

# .python-version 파일 생성
echo "$VIRTUAL_ENV_NAME" > .python-version
echo "폴더 '$TARGET_FOLDER'에서 자동으로 버추얼 환경 '$VIRTUAL_ENV_NAME' 활성화 설정 완료."


# 쉘 갱신
if [ -n "$ZSH_VERSION" ]; then
    echo "zsh 환경 갱신 중..."
    source ~/.zshrc
elif [ -n "$BASH_VERSION" ]; then
    echo "bash 환경 갱신 중..."
    source ~/.bashrc
else
    echo "쉘 환경 갱신을 위해 터미널을 다시 실행하세요."
fi

# 스크립트 완료 메시지
echo "설정이 완료되었습니다. 폴더 '$TARGET_FOLDER'로 이동하면 버추얼 환경이 자동 활성화됩니다."