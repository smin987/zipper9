"""
압축 해제 중단/취소 시 불완전 파일 및 잔여 디렉터리 자동 롤백 클린업 단위 테스트
"""

import os
import shutil
import tempfile
import unittest
import zipfile

from zipper9_ui.bridge.worker import CompressionWorker, list_archive_entries


class TestCancelCleanup(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="zipper9_test_cleanup_")
        self.archive_path = os.path.join(self.test_dir, "sample.zip")
        self.extract_dir = os.path.join(self.test_dir, "extracted")
        os.makedirs(self.extract_dir, exist_ok=True)

        # 1. 테스트용 zip 아카이브 생성 (2개 파일 포함)
        with zipfile.ZipFile(self.archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("large_game_data.wbfs", b"WII_GAME_DATA_" * 100000) # 약 1.4MB
            zf.writestr("manual.txt", b"Game manual instructions.")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cleanup_removes_non_zero_incomplete_files(self):
        """압축 해제 도중 중단되어 생성된 0바이트 초과 불완전 대용량 파일이 자동 삭제되는지 검증"""
        worker = CompressionWorker()

        # 해제 디렉터리에 45% 지점 쓰이다 만 상태를 시뮬레이션 (1MB 크기의 불완전 파일 생성)
        target_file = os.path.join(self.extract_dir, "large_game_data.wbfs")
        with open(target_file, "wb") as f:
            f.write(b"INCOMPLETE_CHUNKS_" * 50000) # 0바이트가 아닌 약 900KB

        self.assertTrue(os.path.exists(target_file), "시뮬레이션 파일이 생성되어야 함")
        self.assertGreater(os.path.getsize(target_file), 0, "파일 크기가 0보다 커야 함")

        # 클린업 실행
        worker._cleanup_corrupted_extractions(self.extract_dir, self.archive_path)

        # 검증: 크기가 0이 아니었음에도 불완전 파일이 완전히 삭제되어야 함!
        self.assertFalse(os.path.exists(target_file), "중단된 불완전 파일은 크기와 무관하게 자동 삭제되어야 합니다!")

        # 검증: 내부가 비워진 extract_dir 폴더 자체도 삭제되어야 함!
        self.assertFalse(os.path.exists(self.extract_dir), "비어있는 해제 폴더도 디스크에 남지 않고 자동 삭제되어야 합니다!")

    def test_cleanup_fallback_when_entries_unknown(self):
        """아카이브 정보를 읽을 수 없는 극단적 상황에서도 output_dir 내 잔여 불완전 파일 정리 검증"""
        worker = CompressionWorker()

        sub_folder = os.path.join(self.extract_dir, "sub")
        os.makedirs(sub_folder, exist_ok=True)
        dummy_file = os.path.join(sub_folder, "corrupted.bin")
        with open(dummy_file, "wb") as f:
            f.write(b"DUMMY_CORRUPTED_BYTES" * 1000)

        # 잘못된 아카이브 경로 전달
        invalid_archive = os.path.join(self.test_dir, "non_existent.zip")
        worker._cleanup_corrupted_extractions(self.extract_dir, invalid_archive)

        self.assertFalse(os.path.exists(dummy_file), "폴더 내 불완전 파일이 삭제되어야 합니다.")
        self.assertFalse(os.path.exists(self.extract_dir), "잔여 폴더도 자동 삭제되어야 합니다.")


if __name__ == "__main__":
    unittest.main()
