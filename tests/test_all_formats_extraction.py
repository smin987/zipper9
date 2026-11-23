"""Test verification for all supported extraction formats in zipper9."""

import os
import sys
import tempfile
import unittest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from zipper9_ui.bridge.worker import SUPPORTED_EXTRACT_EXTS, CompressionWorker
from zipper9_ui.app import is_archive_file, get_file_type_badge
from zipper9_ui.bridge.context_menu import ARCHIVE_EXTENSIONS
from zipper9_ui.bridge.file_association import SUPPORTED_ARCHIVE_EXTS


class TestAllFormatsExtraction(unittest.TestCase):
    def test_extension_coverage(self):
        """사용자가 질의한 모든 포맷이 SUPPORTED_EXTRACT_EXTS에 포함되어 있는지 검증"""
        required_exts = [
            # 표준 압축
            ".zip", ".zipx", ".7z", ".rar", ".tar", ".cab", ".wim", ".sfx", ".sfx.exe",
            # Unix / Linux 계열
            ".gz", ".tgz", ".bz", ".bz2", ".tbz", ".tbz2", ".xz", ".txz",
            ".lzma", ".tlz", ".z", ".taz", ".deb", ".udeb", ".rpm", ".cpio", ".arj",
            # 디스크 이미지
            ".iso", ".img", ".bin", ".udf", ".dmg", ".pkg", ".xip", ".vhd", ".vhdx", ".vmdk",
            # 인스톨러/시스템
            ".msi", ".msp", ".msm",
            # 구형 아카이브
            ".lha", ".lzh", ".alz",
            # 초고속 현대 알고리즘
            ".zst", ".lz4",
        ]
        for ext in required_exts:
            self.assertIn(ext, SUPPORTED_EXTRACT_EXTS, f"Missing {ext} in SUPPORTED_EXTRACT_EXTS")

    def test_is_archive_file_for_all_formats(self):
        """실제 파일 경로 기반 is_archive_file 판정 검증"""
        test_exts = [
            "zipx", "bz", "tbz", "lzma", "tlz", "z", "deb", "arj",
            "img", "bin", "udf", "vhd", "vmdk", "msi", "lha", "lzh", "sfx.exe"
        ]
        for ext in test_exts:
            with tempfile.NamedTemporaryFile(suffix="." + ext, delete=False) as f:
                path = f.name
            try:
                self.assertTrue(is_archive_file(path), f"is_archive_file failed for .{ext}")
            finally:
                os.remove(path)

    def test_context_menu_extensions_coverage(self):
        """우클릭 메뉴 확장자 목록에 신규 포맷이 등록되어 있는지 검증"""
        for ext in [".zipx", ".deb", ".iso", ".dmg", ".img", ".vhd", ".vmdk", ".msi", ".lha", ".lzh"]:
            self.assertIn(ext, ARCHIVE_EXTENSIONS, f"Missing {ext} in context menu ARCHIVE_EXTENSIONS")

    def test_file_association_system_protection_coverage(self):
        """아이콘 파일 연결 목록(SUPPORTED_ARCHIVE_EXTS): 순수 아카이브 36종 포함 및 시스템 포맷(ISO/MSI/VHD 등) 안전 제외 검증"""
        # 1. 순수 아카이브 및 패키지 36종 대폭 확장 포함 확인 (.iso는 디스크 마운트 보존을 위해 제외)
        expected_archive_exts = [
            ".zip", ".zipx", ".7z", ".rar", ".tar", ".cab", ".wim", ".sfx",
            ".gz", ".tgz", ".bz", ".bz2", ".tbz", ".tbz2", ".xz", ".txz",
            ".lzma", ".tlz", ".z", ".taz", ".deb", ".udeb", ".rpm", ".cpio", ".arj",
            ".img", ".bin", ".udf", ".dmg", ".pkg", ".xip",
            ".lha", ".lzh", ".alz", ".lz4", ".zst"
        ]
        for ext in expected_archive_exts:
            self.assertIn(ext, SUPPORTED_ARCHIVE_EXTS, f"Missing {ext} in SUPPORTED_ARCHIVE_EXTS")

        # 2. Windows 디스크 마운트/인스톨러/가상디스크 전용 포맷 안전 제외 확인
        system_protected_exts = [".iso", ".msi", ".msp", ".msm", ".vhd", ".vhdx", ".vmdk", ".vdi", ".qcow2", ".sfx.exe"]
        for ext in system_protected_exts:
            self.assertNotIn(ext, SUPPORTED_ARCHIVE_EXTS, f"{ext} must NOT be in SUPPORTED_ARCHIVE_EXTS for system safety")

    def test_split_archive_badge_and_association(self):
        """분할 압축 아카이브(.001, .7z.001, .zip.001 등)의 아이콘 연결 및 스마트 뱃지 정상 판별 검증"""
        # 1. 파일 확장자 연결 목록(SUPPORTED_ARCHIVE_EXTS) 및 해제 지원 목록에 .001 포함 확인
        self.assertIn(".001", SUPPORTED_ARCHIVE_EXTS, ".001 확장자가 탐색기 아이콘 연결 목록에 포함되어야 함")
        self.assertIn(".001", SUPPORTED_EXTRACT_EXTS, ".001 확장자가 압축 해제 포맷 목록에 포함되어야 함")

        # 2. get_file_type_badge 판별: mame.7z.001 등이 일반 파일이 아닌 '🗜️ 압축'으로 정확히 반환되는지 확인
        test_split_files = [
            "mame.7z.001",
            "archive.zip.001",
            "backup.tar.001",
            "split_game.001",
            "data.z01",
        ]
        for fname in test_split_files:
            badge_text, badge_color = get_file_type_badge(fname)
            self.assertEqual(badge_text, "🗜️ 압축", f"{fname}은 '🗜️ 압축' 뱃지가 부여되어야 함 (실제: {badge_text})")
            self.assertEqual(badge_color, "#ff922b", f"{fname}의 뱃지 컬러가 #ff922b(Coral Orange)여야 함")


if __name__ == "__main__":
    unittest.main()
