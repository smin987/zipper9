"""zipper9 설정 저장 및 로드 관리 모듈.

사용자가 변경한 마지막 세팅값(테마, 알고리즘, 분할 압축, 파일명 암호화, 창 크기 등)을
JSON 파일로 영구 저장하여 다음 실행 시 완벽히 복원합니다.
"""

import json
import os
import sys
from typing import Any, Dict

DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "Dark",
    "lang": "EN",
    "selected_algo": "zstd",
    "extra_algo": "Choose other compression algorithms...",
    "split_preset": "No Splitting (Default)",
    "encrypt_filenames": False,
    "settings_expanded": False,
    "window_geometry": "760x580",
    "context_menu": True,
}


def get_settings_file_path() -> str:
    """설정 파일 경로 반환 (포터블 우선 -> %APPDATA%\\zipper9 폴백)"""
    # 1. 실행 파일과 같은 위치에 'zipper9_settings.json'이 존재하면 포터블 우선 사용
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    portable_path = os.path.join(base_dir, "zipper9_settings.json")
    if os.path.isfile(portable_path):
        return portable_path

    # 2. 기본값: %APPDATA%\zipper9\settings.json
    app_data = os.environ.get("APPDATA")
    if not app_data:
        app_data = os.path.expanduser("~")
    conf_dir = os.path.join(app_data, "zipper9")
    try:
        os.makedirs(conf_dir, exist_ok=True)
        return os.path.join(conf_dir, "settings.json")
    except Exception:
        return portable_path


def load_settings() -> Dict[str, Any]:
    """저장된 설정을 로드합니다. 파일이 없거나 오류 발생 시 기본값을 반환합니다."""
    settings = dict(DEFAULT_SETTINGS)
    path = get_settings_file_path()

    if not os.path.isfile(path):
        return settings

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                # 구버전의 지나치게 큰 900x700 기본값 마이그레이션
                if data.get("window_geometry") == "900x700":
                    data["window_geometry"] = "780x560"
                settings.update(data)
    except Exception as e:
        print(f"[설정 로드 경고] {e}")

    return settings


def save_settings(settings: Dict[str, Any]) -> bool:
    """설정을 JSON 파일로 안전하게 저장합니다."""
    path = get_settings_file_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        if os.path.exists(path):
            os.remove(path)
        os.rename(tmp_path, path)
        return True
    except Exception as e:
        print(f"[설정 저장 실패] {e}")
        return False
