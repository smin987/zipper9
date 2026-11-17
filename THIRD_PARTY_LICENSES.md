# Third-Party Software Notices and Licenses

This project (`zipper9`) bundles, interfaces with, or utilizes several third-party libraries and standalone binaries.
Below are the copyright notices and license terms for these components.

---

## 1. 7-Zip & unRAR

- **Component**: `tools/7z/7z.exe`, `tools/7z/7z.dll`
- **Author**: Igor Pavlov (7-Zip), Alexander Roshal (unRAR portion)
- **Website**: https://www.7-zip.org
- **License**: GNU LGPL v2.1+ with unRAR restriction

### unRAR License Restriction Notice
The 7-Zip source code is released under the GNU LGPL license, except for the unRAR portion.
The unRAR portion cannot be used to re-create the RAR compression algorithm, which is proprietary.
Distribution of modified unRAR source code in separate form is strictly prohibited without written permission from the copyright holder (Alexander Roshal).

`zipper9` only uses 7-Zip for decompression and does not implement or distribute any proprietary RAR compression algorithm.

---

## 2. LZ4

- **Component**: `tools/lz4/lz4.exe`
- **Author**: Yann Collet
- **Website**: https://lz4.github.io/lz4/
- **License**: 
  - Library (`liblz4`): BSD 2-Clause License
  - Command Line Interface (`lz4.exe`): GNU GPL v2.0 License

`zipper9` executes `lz4.exe` as an independent external process via standard IPC pipes. It does not statically or dynamically link to `lz4.exe` internal symbols.

---

## 3. Zstandard (zstd)

- **Component**: `tools/zstd/zstd.exe`
- **Author**: Meta Platforms, Inc. (formerly Facebook, Inc.)
- **Website**: https://facebook.github.io/zstd/
- **License**: BSD 3-Clause License / GPL v2.0 (Dual License - zipper9 adopts BSD 3-Clause)

---

## 4. CustomTkinter

- **Component**: Python GUI Framework
- **Author**: Tom Schimansky
- **Website**: https://github.com/TomSchimansky/CustomTkinter
- **License**: Creative Commons Zero v1.0 Universal (CC0) / MIT License

---

## 5. Windnd

- **Component**: Windows Drag & Drop Hook
- **Author**: Harvey Bao
- **Website**: https://github.com/harveybao/windnd
- **License**: MIT License

---

## 6. DarkDetect

- **Component**: OS Dark Mode Detection
- **Author**: Alberto Sottile
- **Website**: https://github.com/albertopol/darkdetect
- **License**: BSD 3-Clause License

---

## 7. Rust Crates

All Rust dependencies utilized in `zipper9_core` and `zipper9_shell` (`pyo3`, `flate2`, `zstd`, `rayon`, `thiserror`, `zip`, `windows-sys`, `walkdir`) are licensed under standard permissive licenses (**MIT License** and/or **Apache License 2.0**).
