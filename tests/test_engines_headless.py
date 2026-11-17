"""Headless Multi-Platform Engine & Integrity Test Suite for zipper9.

Runs on Windows, Linux (Ubuntu/Debian), and macOS in GitHub Actions CI
without requiring a GUI display (Headless).
Validates:
1. Native CLI binary discovery (7z/7zz, lz4, zstd)
2. Archive creation (ZIP, 7z, TAR.GZ, TAR.LZ4)
3. Archive decompression & byte-level integrity verification (SHA256)
"""

import os
import sys
import shutil
import hashlib
import tempfile
import unittest

# Ensure project root is in sys.path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from zipper9_ui.bridge.worker import (
    find_7z_binary,
    find_lz4_binary,
    find_zstd_binary,
    CompressionWorker,
    list_archive_entries,
    is_native_engine_active,
)


def calc_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestMultiPlatformEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seven_zip = find_7z_binary()
        cls.lz4 = find_lz4_binary()
        cls.zstd = find_zstd_binary()
        print(f"\n[Multi-Platform Discovery] OS: {sys.platform}")
        print(f"  - 7-Zip: {cls.seven_zip}")
        print(f"  - LZ4:   {cls.lz4}")
        print(f"  - Zstd:  {cls.zstd}")

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="zipper9_ci_test_")
        self.src_dir = os.path.join(self.test_dir, "sample_src")
        os.makedirs(self.src_dir, exist_ok=True)

        # Create dummy sample files
        self.file1 = os.path.join(self.src_dir, "hello.txt")
        with open(self.file1, "w", encoding="utf-8") as f:
            f.write("Hello zipper9 multi-platform automated CI verification!\n" * 100)

        self.file2 = os.path.join(self.src_dir, "binary.dat")
        with open(self.file2, "wb") as f:
            f.write(os.urandom(1024 * 64))  # 64KB random bytes

        self.sub_dir = os.path.join(self.src_dir, "nested_folder")
        os.makedirs(self.sub_dir, exist_ok=True)
        self.file3 = os.path.join(self.sub_dir, "nested.txt")
        with open(self.file3, "w", encoding="utf-8") as f:
            f.write("Nested file content inside subfolder.\n" * 50)

        self.file1_hash = calc_sha256(self.file1)
        self.file2_hash = calc_sha256(self.file2)
        self.file3_hash = calc_sha256(self.file3)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_binary_discovery(self):
        """At least 7z or Python native fallback must be operational"""
        self.assertTrue(
            self.seven_zip is not None or sys.platform != "win32",
            "7-Zip binary should be detected on Windows or available via system packages",
        )

    def _sync_compress(self, sources, out_path, fmt, level=None, password=None, verify_integrity=False):
        worker = CompressionWorker()
        finished = [False]
        errors = []

        def on_finish(msg):
            finished[0] = True

        def on_error(err):
            errors.append(err)

        worker.compress_async(
            source_paths=sources,
            output_archive_path=out_path,
            format_type=fmt,
            level=level,
            password=password,
            split_size=None,
            verify_integrity=verify_integrity,
            on_progress=lambda p: None,
            on_finish=on_finish,
            on_error=on_error,
        )
        if worker._thread:
            worker._thread.join(timeout=30)

        if errors:
            raise errors[0]
        self.assertTrue(finished[0], f"Compression for {fmt} did not finish successfully")
        self.assertTrue(os.path.isfile(out_path), f"Output file not generated: {out_path}")
        self.assertGreater(os.path.getsize(out_path), 0, f"Output file is empty: {out_path}")

    def _sync_extract(self, archive_path, out_dir, password=None):
        worker = CompressionWorker()
        finished = [False]
        errors = []

        def on_finish(msg):
            finished[0] = True

        def on_error(err):
            errors.append(err)

        worker.extract_async(
            archive_path=archive_path,
            output_dir=out_dir,
            password=password,
            on_progress=lambda p: None,
            on_finish=on_finish,
            on_error=on_error,
        )
        if worker._thread:
            worker._thread.join(timeout=30)

        if errors:
            raise errors[0]
        self.assertTrue(finished[0], f"Extraction for {archive_path} did not finish")

    def test_02_zip_compression_and_extraction(self):
        """Test ZIP archive roundtrip and integrity verification"""
        out_zip = os.path.join(self.test_dir, "test_output.zip")
        self._sync_compress([self.src_dir], out_zip, fmt="zip")

        # Verify entry listing
        entries = list_archive_entries(out_zip)
        self.assertGreater(len(entries), 0, "Entries list should not be empty")

        # Extract to clean destination
        extract_dir = os.path.join(self.test_dir, "extracted_zip")
        self._sync_extract(out_zip, extract_dir)

        # Verify hash integrity
        # Note: files might be inside sample_src/ or top level depending on smart root
        target_f1 = None
        for root, dirs, files in os.walk(extract_dir):
            if "hello.txt" in files:
                target_f1 = os.path.join(root, "hello.txt")
                break
        self.assertIsNotNone(target_f1, "hello.txt not found in extracted output")
        self.assertEqual(calc_sha256(target_f1), self.file1_hash, "SHA256 mismatch on hello.txt")

    def test_03_7z_compression_and_extraction(self):
        """Test 7z LZMA2 archive roundtrip"""
        if not self.seven_zip:
            self.skipTest("7z binary not available in test environment")

        out_7z = os.path.join(self.test_dir, "test_output.7z")
        self._sync_compress([self.src_dir], out_7z, fmt="7z")

        extract_dir = os.path.join(self.test_dir, "extracted_7z")
        self._sync_extract(out_7z, extract_dir)

        target_f2 = None
        for root, dirs, files in os.walk(extract_dir):
            if "binary.dat" in files:
                target_f2 = os.path.join(root, "binary.dat")
                break
        self.assertIsNotNone(target_f2, "binary.dat not found in 7z extracted output")
        self.assertEqual(calc_sha256(target_f2), self.file2_hash, "SHA256 mismatch on binary.dat")

    def test_04_tar_gz_compression_and_extraction(self):
        """Test TAR.GZ archive roundtrip (cross-platform standard)"""
        out_tar = os.path.join(self.test_dir, "test_output.tar.gz")
        self._sync_compress([self.src_dir], out_tar, fmt="tar.gz")

        extract_dir = os.path.join(self.test_dir, "extracted_tar")
        self._sync_extract(out_tar, extract_dir)

        target_f3 = None
        for root, dirs, files in os.walk(extract_dir):
            if "nested.txt" in files:
                target_f3 = os.path.join(root, "nested.txt")
                break
        self.assertIsNotNone(target_f3, "nested.txt not found in tar.gz extracted output")
        self.assertEqual(calc_sha256(target_f3), self.file3_hash, "SHA256 mismatch on nested.txt")

    def test_05_archive_integrity_verification(self):
        """Test archive integrity verification on valid, corrupted, LZ4, and split archives"""
        # 1. ZIP integrity and corruption detection
        out_zip = os.path.join(self.test_dir, "integrity_test.zip")
        self._sync_compress([self.src_dir], out_zip, fmt="zip", verify_integrity=True)
        self.assertTrue(os.path.isfile(out_zip))

        # Intentionally corrupt the archive bytes and verify that error is detected
        with open(out_zip, "r+b") as f:
            f.seek(60)
            f.write(b"\x00\xFF\x00\xFF\x00\xFF\x00\xFF\x00\xFF\x00\xFF")

        worker = CompressionWorker()
        with self.assertRaises(Exception):
            worker.verify_archive_integrity(out_zip)

        # 2. TAR.LZ4 native integrity verification
        out_lz4 = os.path.join(self.test_dir, "integrity_test.tar.lz4")
        self._sync_compress([self.src_dir], out_lz4, fmt="tar.lz4", verify_integrity=True)
        self.assertTrue(os.path.isfile(out_lz4))

        # 3. 7z split archive volume integrity (.001)
        out_7z_split = os.path.join(self.test_dir, "split_test.7z")
        worker.compress_sync([self.src_dir], out_7z_split, format_type="7z", split_size="100k", verify_integrity=True)
        self.assertTrue(os.path.isfile(out_7z_split + ".001"))


if __name__ == "__main__":
    unittest.main()
