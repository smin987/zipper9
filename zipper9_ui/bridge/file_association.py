"""zipper9 Windows 파일 확장자 및 압축 아이콘 연결 관리 모듈.

Windows 탐색기 상에서 .zip, .7z, .rar, .tar 등의 압축 파일들이
zipper9의 세련된 전용 압축 아이콘으로 별도 표시되도록
HKCU\\Software\\Classes 레지스트리에 DefaultIcon 및 ProgID를 등록/해제합니다.
"""

import os
import sys

if sys.platform == "win32":
    import winreg
    import ctypes
else:
    winreg = None
    ctypes = None

SUPPORTED_ARCHIVE_EXTS = [
    ".zip",
    ".zipx",
    ".7z",
    ".rar",
    ".tar",
    ".gz",
    ".xz",
    ".bz2",
    ".lz4",
    ".zst",
    ".tgz",
    ".iso",
    ".dmg",
    ".alz",
    ".egg",
]

PROGID = "zipper9.Archive"
PROGID_NAME = "zipper9 압축 아카이브"


def get_base_dir() -> str:
    """프로젝트 루트 기본 디렉터리 경로 반환"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    cur = os.path.abspath(__file__)
    # zipper9_ui/bridge/file_association.py -> 3단계 상위가 루트
    return os.path.dirname(os.path.dirname(os.path.dirname(cur)))


def get_icon_path() -> str:
    """압축 파일 전용 아이콘 (.ico) 절대 경로 반환"""
    base_dir = get_base_dir()
    
    # 1순위: assets/archive_icon.ico (전용 압축 아이콘)
    archive_ico = os.path.join(base_dir, "assets", "archive_icon.ico")
    if os.path.exists(archive_ico):
        return f"{archive_ico},0"
        
    # 2순위: assets/zipper9.ico
    zipper9_ico = os.path.join(base_dir, "assets", "zipper9.ico")
    if os.path.exists(zipper9_ico):
        return f"{zipper9_ico},0"
        
    # 3순위: 실행 바이너리 리소스
    exe_path = os.path.join(base_dir, "dist", "zipper9.exe")
    if os.path.exists(exe_path):
        return f"{exe_path},0"
        
    if getattr(sys, "frozen", False):
        return f"{sys.executable},0"
        
    return ""


def get_exe_path() -> str:
    """실행 파일 절대 경로 반환"""
    if getattr(sys, "frozen", False):
        return sys.executable
    base_dir = get_base_dir()
    exe_path = os.path.join(base_dir, "dist", "zipper9.exe")
    if os.path.exists(exe_path):
        return exe_path
    return sys.executable


def refresh_shell_icons():
    """Windows 탐색기 아이콘 캐시 즉시 갱신 (SHChangeNotify)"""
    try:
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    except Exception as e:
        print(f"Shell refresh error: {e}")


def _delete_key_tree(root, subkey):
    """하위 키를 재귀적으로 삭제"""
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            while True:
                try:
                    sub = winreg.EnumKey(key, 0)
                    _delete_key_tree(root, f"{subkey}\\{sub}")
                except OSError:
                    break
        winreg.DeleteKey(root, subkey)
    except OSError:
        pass


def register_file_associations(icon_path: str | None = None) -> bool:
    """압축 파일 확장자들에 대해 zipper9 전용 압축 아이콘 연결 등록"""
    if not winreg:
        return False
    target_icon = icon_path or get_icon_path()
    exe_path = get_exe_path()
    if not target_icon:
        return False

    try:
        # 1. HKCU\Software\Classes\zipper9.Archive 등록
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROGID_NAME)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, target_icon)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')

        # 2. 각 확장자에 연결 및 DefaultIcon 등록
        for ext in SUPPORTED_ARCHIVE_EXTS:
            # HKCU\Software\Classes\<ext>
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}") as key:
                # 기존 값 백업
                try:
                    cur_val, _ = winreg.QueryValueEx(key, "")
                    if cur_val and cur_val != PROGID:
                        winreg.SetValueEx(key, "zipper9_backup_progid", 0, winreg.REG_SZ, cur_val)
                except OSError:
                    pass
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROGID)

            # 탐색기 아이콘 우선 표출을 위한 DefaultIcon 키
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}\DefaultIcon") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, target_icon)

        # 3. 쉘 변경 알림
        refresh_shell_icons()
        return True
    except Exception as e:
        print(f"Error registering file associations: {e}")
        return False


def unregister_file_associations() -> bool:
    """압축 파일 확장자들의 zipper9 전용 압축 아이콘 연결 해제 및 복원"""
    if not winreg:
        return False
    try:
        # 1. 각 확장자에서 복원 또는 삭제
        for ext in SUPPORTED_ARCHIVE_EXTS:
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{ext}\DefaultIcon")
            except OSError:
                pass

            try:
                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    rf"Software\Classes\{ext}",
                    0,
                    winreg.KEY_READ | winreg.KEY_WRITE,
                ) as key:
                    try:
                        cur_val, _ = winreg.QueryValueEx(key, "")
                        if cur_val == PROGID:
                            # 백업 복원 시도
                            try:
                                backup, _ = winreg.QueryValueEx(key, "zipper9_backup_progid")
                                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, backup)
                                winreg.DeleteValue(key, "zipper9_backup_progid")
                            except OSError:
                                winreg.DeleteValue(key, "")
                    except OSError:
                        pass
            except OSError:
                pass

        # 2. HKCU\Software\Classes\zipper9.Archive 키 삭제
        _delete_key_tree(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}")

        # 3. 쉘 변경 알림
        refresh_shell_icons()
        return True
    except Exception as e:
        print(f"Error unregistering file associations: {e}")
        return False


def is_file_associations_registered() -> bool:
    """압축 파일 아이콘 연결이 현재 활성화되어 있는지 확인"""
    if not winreg:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, rf"Software\Classes\{PROGID}\DefaultIcon"
        ) as key:
            val, _ = winreg.QueryValueEx(key, "")
            return bool(val)
    except OSError:
        return False
