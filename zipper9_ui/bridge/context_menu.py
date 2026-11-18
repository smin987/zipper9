"""Windows Context Menu (마우스 우클릭 메뉴) 관리 모듈.

1. Windows 11 모던 1단계 최상위 메뉴 지원:
   - IExplorerCommand COM DLL + Windows 11 전용 패키지(zipper9_shell.msix) 연동
   - 반디집(Bandizip)과 100% 동일한 최상위 메뉴에 직접 노출
2. Windows 10 및 클래식 메뉴 완벽 호환:
   - HKEY_CURRENT_USER\\Software\\Classes 에 등록하여 관리자 권한 없이 안전하게 등록/해제
"""

import os
import subprocess
import sys
from typing import List, Optional

if sys.platform == "win32":
    import winreg
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUP_INFO.wShowWindow = 0  # SW_HIDE
else:
    winreg = None
    STARTUP_INFO = None

ARCHIVE_EXTENSIONS: List[str] = [
    ".zip", ".zipx", ".7z", ".rar", ".tar", ".gz", ".tgz",
    ".bz", ".bz2", ".tbz", ".tbz2", ".xz", ".txz", ".zst", ".lz4",
    ".iso", ".img", ".bin", ".udf", ".vhd", ".vhdx", ".vmdk",
    ".cab", ".wim", ".alz", ".deb", ".udeb", ".rpm",
    ".arj", ".lzma", ".tlz", ".z", ".taz", ".lha", ".lzh", ".msi",
    ".dmg", ".pkg", ".xip", ".001", ".z01", ".part1.rar",
]


def get_base_dir() -> str:
    """기본 디렉터리 반환 (frozen 지원)"""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_modern_msix_path() -> Optional[str]:
    """zipper9_shell.msix 파일 경로 탐색"""
    base = get_base_dir()
    cand1 = os.path.join(base, "tools", "zipper9_shell.msix")
    if os.path.isfile(cand1):
        return cand1

    if getattr(sys, "frozen", False):
        cand2 = os.path.join(os.path.dirname(sys.executable), "tools", "zipper9_shell.msix")
        if os.path.isfile(cand2):
            return cand2

    # 프로젝트 개발 루트 기준
    dev_path = r"D:\mirror\dev\MyPython\in_service\zipper9\tools\zipper9_shell.msix"
    if os.path.isfile(dev_path):
        return dev_path

    return None


def is_modern_package_registered() -> bool:
    """Windows 11 모던 패키지 등록 여부 초고속 확인 (레지스트리 1ms 조회 후 폴백)"""
    if sys.platform != "win32":
        return False
    
    # 1. 초고속 winreg 레지스트리 검색 (~1ms)
    if winreg:
        repo_path = r"Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, repo_path) as k:
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(k, i)
                        if name.startswith("zipper9ShellExt"):
                            return True
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass

    # 2. 폴백 PowerShell 검사 (타임아웃 3초 안전 설정)
    try:
        cmd = ["powershell", "-NoProfile", "-Command", "Get-AppxPackage zipper9ShellExt*"]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=3,
            creationflags=0x08000000,
            startupinfo=STARTUP_INFO,
        )
        return "zipper9ShellExt" in res.stdout
    except Exception:
        return False


def register_modern_package() -> bool:
    """Windows 11 모던 1단계 패키지 등록"""
    # 이미 등록되어 있으면 패키징 불필요 (0ms 즉시 통과)
    if is_modern_package_registered():
        return True

    msix = find_modern_msix_path()
    if not msix:
        return False
    try:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-Command", f'Add-AppxPackage -Path "{os.path.abspath(msix)}"'
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
            creationflags=0x08000000,
            startupinfo=STARTUP_INFO,
        )
        return res.returncode == 0 or is_modern_package_registered()
    except Exception:
        return False


def unregister_modern_package() -> bool:
    """Windows 11 모던 패키지 등록 해제"""
    if not is_modern_package_registered():
        return True

    try:
        cmd = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-Command", 'Get-AppxPackage zipper9ShellExt* | Remove-AppxPackage -Confirm:$false'
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=10,
            creationflags=0x08000000,
            startupinfo=STARTUP_INFO,
        )
        return res.returncode == 0 or not is_modern_package_registered()
    except Exception:
        return False


def refresh_shell():
    """Windows 탐색기에 셸 변경 알림 (SHChangeNotify - 탐색기 재시작 없이 즉시 반영)"""
    try:
        import ctypes
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    except Exception:
        pass


def get_invoker_command() -> tuple[str, str]:
    """우클릭 시 실행할 커맨드 프리픽스와 아이콘 경로 반환"""
    base_dir = get_base_dir()
    dist_exe = os.path.join(base_dir, "dist", "zipper9.exe")

    # 1순위: PyInstaller 바이너리 자체 실행 중
    if getattr(sys, "frozen", False):
        exe_path = os.path.abspath(sys.executable)
        return f'"{exe_path}"', f'"{exe_path}"'

    # 2순위: 파이썬 소스 개발 환경 (run.bat 등)
    main_script = os.path.join(base_dir, "main.py")
    python_dir = os.path.dirname(sys.executable)
    pythonw_candidate = os.path.join(python_dir, "pythonw.exe")
    python_exe = pythonw_candidate if os.path.isfile(pythonw_candidate) else sys.executable

    # 전용 아이콘 탐색
    archive_ico = os.path.join(base_dir, "assets", "archive_icon.ico")
    icon_path = f'"{dist_exe}"' if os.path.isfile(dist_exe) else (f'"{archive_ico}"' if os.path.isfile(archive_ico) else f'"{python_exe}"')

    # dist_exe가 존재하고 소스코드(main.py)보다 최신이면 dist_exe 바인딩
    if os.path.isfile(dist_exe):
        dist_mtime = os.path.getmtime(dist_exe)
        main_mtime = os.path.getmtime(main_script) if os.path.isfile(main_script) else 0
        if dist_mtime >= main_mtime:
            exe_abs = os.path.abspath(dist_exe)
            return f'"{exe_abs}"', f'"{exe_abs}"'

    # 소스코드가 더 최신이거나 dist_exe가 없으면 현재 파이썬 인터프리터 바인딩
    cmd_prefix = f'"{python_exe}" "{main_script}"'
    return cmd_prefix, icon_path


def _delete_key_recursive(root_key, subkey: str) -> bool:
    """하위 키를 포함하여 레지스트리 키 재귀 삭제"""
    if not winreg:
        return False
    try:
        with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
            while True:
                try:
                    child_name = winreg.EnumKey(key, 0)
                    _delete_key_recursive(key, child_name)
                except OSError:
                    break
        winreg.DeleteKey(root_key, subkey)
        return True
    except FileNotFoundError:
        return True
    except Exception:
        return False


def is_context_menu_registered() -> bool:
    """우클릭 메뉴가 현재 등록되어 있는지 확인 (레거시 레지스트리 우선 확인 후 모던 패키지 조회)"""
    if winreg:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\zipper9_compress"):
                return True
        except FileNotFoundError:
            pass
        except Exception:
            pass

    return is_modern_package_registered()


def register_context_menu(custom_exe_path: Optional[str] = None) -> bool:
    """우클릭 메뉴 등록 (Windows 11 모던 1단계 + Windows 10/클래식 레거시 하이브리드 등록)"""
    # 1. Windows 11 모던 패키지 등록 시도 (반디집과 동일한 1단계 메뉴)
    register_modern_package()

    base_dir = get_base_dir()
    dist_exe = os.path.join(base_dir, "dist", "zipper9.exe")

    # zipper9 실행 파일 경로 HKCU\Software\zipper9\ExePath 저장 (모던 셸 익스텐션 DLL용)
    if winreg:
        try:
            if custom_exe_path:
                exe_target = custom_exe_path
            elif getattr(sys, "frozen", False):
                exe_target = sys.executable
            elif os.path.isfile(dist_exe):
                exe_target = dist_exe
            else:
                exe_target = sys.executable
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\zipper9") as z_key:
                winreg.SetValueEx(z_key, "ExePath", 0, winreg.REG_SZ, os.path.abspath(exe_target))
        except Exception:
            pass

    # 2. Windows 10 / 클래식 셸용 레거시 HKCU 등록 (호환성 보장)
    if not winreg:
        return False

    if custom_exe_path:
        exe_abs = os.path.abspath(custom_exe_path)
        cmd_prefix = f'"{exe_abs}"'
        icon_path = f'"{exe_abs}"'
    else:
        cmd_prefix, icon_path = get_invoker_command()

    try:
        # 파일 우클릭: zipper9으로 압축하기
        key_path = r"Software\Classes\*\shell\zipper9_compress"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "⚡ zipper9으로 압축하기")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            with winreg.CreateKey(key, "command") as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'{cmd_prefix} --compress-instant "%1"')

        # 폴더 우클릭: zipper9으로 압축하기 (Directory에만 등록하여 Folder 클래스 상속으로 인한 Background 침범 방지)
        d_key = r"Software\Classes\Directory\shell\zipper9_compress"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, d_key) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "⚡ zipper9으로 압축하기")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            with winreg.CreateKey(key, "command") as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'{cmd_prefix} --compress-instant "%1"')

        # 기존 Folder\shell 키 잔재 삭제 (바탕화면 빈공간에 "압축하기" 노출 방지)
        _delete_key_recursive(winreg.HKEY_CURRENT_USER, r"Software\Classes\Folder\shell\zipper9_compress")

        # 바탕화면 및 폴더 빈공간 우클릭: zipper9 열기
        bg_key_path = r"Software\Classes\Directory\Background\shell\zipper9_open"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, bg_key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "⚡ zipper9 열기")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            with winreg.CreateKey(key, "command") as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'{cmd_prefix}')

        # 압축 확장자별 우클릭: zipper9으로 풀기
        for ext in ARCHIVE_EXTENSIONS:
            assoc_key_path = rf"Software\Classes\SystemFileAssociations\{ext}\shell\zipper9_extract"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, assoc_key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "⚡ zipper9으로 풀기")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
                with winreg.CreateKey(key, "command") as cmd_key:
                    winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'{cmd_prefix} --extract-instant "%1"')

        # 3. Windows 탐색기 셸 변경 즉시 알림 (재시작 없이 즉시 반영)
        refresh_shell()
        return True
    except Exception as e:
        print(f"Failed to register context menu: {e}")
        return False


def unregister_context_menu() -> bool:
    """우클릭 메뉴 완전 삭제 (모던 패키지 및 레거시 레지스트리 동시 제거)"""
    # 1. 모던 패키지 제거
    unregister_modern_package()

    if not winreg:
        return False

    success = True
    if not _delete_key_recursive(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\zipper9_compress"):
        success = False
    if not _delete_key_recursive(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\shell\zipper9_compress"):
        success = False
    if not _delete_key_recursive(winreg.HKEY_CURRENT_USER, r"Software\Classes\Folder\shell\zipper9_compress"):
        success = False
    if not _delete_key_recursive(winreg.HKEY_CURRENT_USER, r"Software\Classes\Directory\Background\shell\zipper9_open"):
        success = False
    for ext in ARCHIVE_EXTENSIONS:
        assoc_key_path = rf"Software\Classes\SystemFileAssociations\{ext}\shell\zipper9_extract"
        if not _delete_key_recursive(winreg.HKEY_CURRENT_USER, assoc_key_path):
            success = False

    # Windows 탐색기 셸 변경 즉시 알림
    refresh_shell()
    return success
