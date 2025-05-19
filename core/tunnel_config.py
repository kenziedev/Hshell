# core/tunnel_config.py
# 서버 목록을 JSON 파일에서 로드/저장하는 기능을 담당

import json
import os
import sys

def get_app_data_dir():
    """
    애플리케이션 데이터 디렉토리 경로를 반환합니다.
    개발 환경에서는 프로젝트 루트의 data 디렉토리를,
    실행 파일에서는 실행 파일이 있는 디렉토리의 data 디렉토리를 사용합니다.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        app_dir = os.path.dirname(sys.executable)
    else:
        # 개발 환경
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    data_dir = os.path.join(app_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    return data_dir

# 서버 목록 파일 경로
DATA_FILE = os.path.join(get_app_data_dir(), 'servers.json')

def load_server_list():
    """
    JSON 파일에서 서버 목록을 불러온다.
    파일이 없으면 빈 리스트를 반환.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ 서버 설정 파일이 손상되었거나 잘못된 형식입니다.")
        return []
    except Exception as e:
        print(f"⚠️ 서버 설정 파일을 불러오는 중 오류 발생: {e}")
        return []

def save_server_list(server_list):
    """
    서버 목록을 JSON 파일에 저장한다.
    
    :param server_list: 서버 딕셔너리 리스트
    """
    try:
        # 데이터 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(server_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ 서버 설정 파일을 저장하는 중 오류 발생: {e}")
        raise
