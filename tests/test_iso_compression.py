"""Test ISO (UDF) compression, integrity verification, extraction, and UI integration."""

import os
import sys
import shutil
import tempfile
import unittest

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from zipper9_ui.bridge.worker import CompressionWorker
from zipper9_ui.bridge.i18n import t
from zipper9_ui.app import is_archive_file, EXTRA_ALGO_KEYS


class TestISOCompression(unittest.TestCase):
    def setUp(self):
        self.worker = CompressionWorker()
        self.test_dir = tempfile.mkdtemp(prefix="zipper9_iso_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_iso_udf_creation_and_extraction(self):
        """ISO (UDF) 압축 생성, 무결성 검증, 압축 해제 및 바이트 일치성 검증"""
        # 1. 테스트 소스 파일 및 중첩 디렉터리 구성 (한글, 긴 이름, 특수문자)
        src_dir = os.path.join(self.test_dir, "sources")
        os.makedirs(src_dir, exist_ok=True)

        file1 = os.path.join(src_dir, "test_file.txt")
        with open(file1, "wb") as f:
            f.write(b"Hello ISO UDF world! 1234567890")

        hangul_dir = os.path.join(src_dir, "한글 폴더 디렉터리 (특수문자 포함)")
        os.makedirs(hangul_dir, exist_ok=True)
        file2 = os.path.join(hangul_dir, "한글_문서_테스트_2026.docx")
        with open(file2, "wb") as f:
            f.write(b"UTF-8 Hangul Content Inside UDF ISO Image.")

        deep_dir = os.path.join(hangul_dir, "Deep_Level_3", "Deep_Level_4")
        os.makedirs(deep_dir, exist_ok=True)
        file3 = os.path.join(deep_dir, "very_deep_file.log")
        with open(file3, "wb") as f:
            f.write(b"Deep nesting log data.")

        # 2. 동기 ISO 생성
        iso_output = os.path.join(self.test_dir, "output.iso")
        self.worker.compress_sync(
            source_paths=[file1, hangul_dir],
            output_archive_path=iso_output,
            format_type="iso",
        )

        self.assertTrue(os.path.isfile(iso_output))
        self.assertGreater(os.path.getsize(iso_output), 0)
        self.assertTrue(is_archive_file(iso_output))

        # 3. 7-Zip 엔진을 통한 아카이브 무결성 검증 (7z t)
        self.assertTrue(self.worker.verify_archive_integrity(iso_output))

        # 4. 압축 해제 검증
        extract_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        self.worker.extract_sync(
            archive_path=iso_output,
            output_dir=extract_dir,
        )

        # 5. 복원된 파일 및 내용 검증
        ext_file1 = os.path.join(extract_dir, "test_file.txt")
        self.assertTrue(os.path.isfile(ext_file1), f"Missing {ext_file1}")
        with open(ext_file1, "rb") as f:
            self.assertEqual(f.read(), b"Hello ISO UDF world! 1234567890")

        ext_hangul_dir = os.path.join(extract_dir, "한글 폴더 디렉터리 (특수문자 포함)")
        self.assertTrue(os.path.isdir(ext_hangul_dir), f"Missing {ext_hangul_dir}")

        ext_file2 = os.path.join(ext_hangul_dir, "한글_문서_테스트_2026.docx")
        self.assertTrue(os.path.isfile(ext_file2), f"Missing {ext_file2}")
        with open(ext_file2, "rb") as f:
            self.assertEqual(f.read(), b"UTF-8 Hangul Content Inside UDF ISO Image.")

        ext_file3 = os.path.join(ext_hangul_dir, "Deep_Level_3", "Deep_Level_4", "very_deep_file.log")
        self.assertTrue(os.path.isfile(ext_file3), f"Missing {ext_file3}")
        with open(ext_file3, "rb") as f:
            self.assertEqual(f.read(), b"Deep nesting log data.")

    def test_ui_and_i18n_integration(self):
        """추가 알고리즘 드롭다운 및 다국어 매핑에 ISO가 정상 등록되어 있는지 검증"""
        self.assertIn("algo_extra_iso", EXTRA_ALGO_KEYS)

        # KO 및 EN 텍스트 확인
        ko_text = t("algo_extra_iso", lang="KO")
        en_text = t("algo_extra_iso", lang="EN")
        self.assertIn("ISO", ko_text)
        self.assertIn("UDF", ko_text)
        self.assertIn("ISO", en_text)
        self.assertIn("UDF", en_text)


if __name__ == "__main__":
    unittest.main()
