import os
import sys


def _get_app_root_dir():
    """
    실행 형태(개발/배포)에 따라 애플리케이션 루트 디렉토리를 반환합니다.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_data_dir() -> str:
    """
    영속 데이터를 저장할 디렉토리를 반환하며, 없으면 생성합니다.
    """
    data_dir = os.path.join(_get_app_root_dir(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

