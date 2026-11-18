"""Test verification for all supported extraction formats in zipper9."""

import os
import sys
import tempfile
import unittest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from zipper9_ui.bridge.worker import SUPPORTED_EXTRACT_EXTS, CompressionWorker
from zipper9_ui.app import is_archive_file
from zipper9_ui.bridge.context_menu import ARCHIVE_EXTENSIONS


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
            ".lha", ".lzh", ".alz", ".egg",
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


if __name__ == "__main__":
    unittest.main()
