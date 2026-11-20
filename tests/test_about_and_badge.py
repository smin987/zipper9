"""test_about_and_badge.py: 정보/라이선스 다이얼로그, 툴팁 및 버전 뱃지 동작 검증 단위 테스트."""

import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import customtkinter as ctk

from zipper9_ui.app import Zipper9App, APP_VERSION
from zipper9_ui.about_dialog import AboutLicenseDialog
from zipper9_ui.tooltip import ModernTooltip
from zipper9_ui.bridge.i18n import t, set_language


class TestAboutAndBadge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_version_comparison_logic(self):
        """버전 문자열 비교 로직 검증"""
        self.assertTrue(Zipper9App._is_newer_version("v1.0.1", "v1.0.0"))
        self.assertTrue(Zipper9App._is_newer_version("1.1.0", "v1.0.0"))
        self.assertTrue(Zipper9App._is_newer_version("v2.0.0", "1.0.0"))
        self.assertFalse(Zipper9App._is_newer_version("v1.0.0", "v1.0.0"))
        self.assertFalse(Zipper9App._is_newer_version("v0.9.9", "v1.0.0"))
        self.assertFalse(Zipper9App._is_newer_version("invalid", "v1.0.0"))

    def test_tooltip_functionality(self):
        """ModernTooltip 생성 및 텍스트 콜백 검증"""
        btn = ctk.CTkButton(self.root, text="Test")
        tooltip_text = "테스트 툴팁입니다."
        tip = ModernTooltip(btn, lambda: tooltip_text, delay_ms=50)
        self.assertEqual(tip._get_text(), tooltip_text)

        # 텍스트 동적 변경 검증
        tooltip_text = "새로운 툴팁 텍스트"
        self.assertEqual(tip._get_text(), tooltip_text)

    def test_about_license_dialog_creation(self):
        """AboutLicenseDialog 팝업 정상 생성 및 텍스트 요소 확인"""
        with patch.object(AboutLicenseDialog, "grab_set", return_value=None):
            dialog = AboutLicenseDialog(self.root, APP_VERSION)
            self.assertIsNotNone(dialog)
            self.assertIn("zipper9", dialog.title())

            # URL 열기 검증
            with patch("webbrowser.open") as mock_open:
                dialog._open_repo()
                mock_open.assert_called_with("https://github.com/smin987/zipper9")

                dialog._open_license_file()
                mock_open.assert_called_with("https://github.com/smin987/zipper9/blob/main/LICENSE")

            dialog.destroy()


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAboutAndBadge)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()
