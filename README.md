# zipper9 (Ultra-Lightweight Multi-Format Archiver) - v1.0.1

<div align="center">

<p>
  <b>English</b> • <a href="README.ko.md"><b>한국어 (Korean)</b></a>
</p>

[![License](https://img.shields.io/badge/License-Fair--code-blue.svg)](LICENSE)
[![Source](https://img.shields.io/badge/Source-Available-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#-quick-install--run)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-ff69b4.svg)](#-support--sponsorship)

**Ultra-Lightweight & Blazing-Fast Cross-Platform Archiver powered by Native C/C++ Engines**  
*Compact bundle, Zstandard / LZ4 / LZMA2 multi-core compression, and modern Windows 11 shell integration.*

[Screenshots](#-screenshots) • [Key Features](#-key-features) • [Quick Install](#-quick-install--run) • [FAQ](#-faq--troubleshooting) • [Sponsor](#-support--sponsorship) • [License](#-license)

</div>

---

## 🌟 Key Features

### 📸 Screenshots

<div align="center">

#### ☀️ Light Mode
| Compact View (Settings Collapsed) | Detailed View (Settings Expanded) |
| :---: | :---: |
| <a href="images/1.0.1/screenshot_en_normal_collapsed.png"><img src="images/1.0.1/screenshot_en_normal_collapsed.png" alt="zipper9 English Light Mode (Collapsed)" width="450"></a> | <a href="images/1.0.1/screenshot_en_normal.png"><img src="images/1.0.1/screenshot_en_normal.png" alt="zipper9 English Light Mode (Expanded)" width="450"></a> |

#### 🌙 Dark Mode
| Compact View (Settings Collapsed) | Detailed View (Settings Expanded) |
| :---: | :---: |
| <a href="images/1.0.1/screenshot_en_dark_collapsed.png"><img src="images/1.0.1/screenshot_en_dark_collapsed.png" alt="zipper9 English Dark Mode (Collapsed)" width="450"></a> | <a href="images/1.0.1/screenshot_en_dark.png"><img src="images/1.0.1/screenshot_en_dark.png" alt="zipper9 English Dark Mode (Expanded)" width="450"></a> |

*💡 Easily toggle between Light and Dark mode via the header switch, or collapse settings (▼/▶) for an ultra-compact window (820px ➔ 580px).*

</div>

1. **Ultra-Lightweight Modern UI (CustomTkinter)**:
   - Compact standalone bundle (~18MB), instant responsiveness, and polished Dark/Light theme support.
   - **Full Drag & Drop** for files and folders, and instant archive inspection for ZIP, 7z, and TAR archives.
   - Individual item removal with **`[✕]` button** directly from the source list.
   - **Real-time English / Korean language toggle** on the fly.
2. **Comprehensive Format & High-Speed Algorithm Support**:
   - **ZIP Archives (`.zip`)**:
     - `Zstandard (zstd)`: Meta's modern balanced high-speed & high-ratio algorithm (Default; 3-5x faster compression, 5-10x faster decompression than standard Deflate).
     - `Store (Uncompressed)`: Ultra-fast packaging within seconds for pre-compressed media files (videos, photos, archives).
   - **7-Zip Archives (`.7z`)**:
     - `7z: LZMA2 (Standard)`: Multi-threaded standard high-ratio compression powered by the native 7-Zip engine.
   - **TAR Archives (Unix / Linux / macOS Standard)**:
     - `TAR: .tar.lz4`: **LZ4 Ultra-Fast Archiving** (Decompression at RAM-bus speeds; ideal for large backups, VM disks, and game assets).
     - `TAR: .tar.gz`: Universal Unix/Linux/macOS standard tarball distribution format.
     - `TAR: .tar.xz`: Modern Linux kernel and packaging standard (XZ / LZMA2).
     - `TAR: .tar.bz2`: Classic Linux archive format (Bzip2).
     - `TAR: .tar`: Raw uncompressed tarball packaging.
3. **Archive Inspection & Safe Extraction**:
   - Real-time pre-extraction analysis: internal file tree, original size, compressed size, and savings percentage (%).
   - Built-in defenses against **Zip-Slip** and **Tar-Slip** path-traversal directory escape vulnerabilities.
   - Smart single-root folder extraction (Bandizip-style duplicate directory suppression).
4. **Post-Compression Integrity Verification**:
   - Enable **`[Verify integrity after compression]`** to automatically validate archive headers, CRC32/SHA checksums, and frame integrity immediately after compression via native 7-Zip (`7z t`) and LZ4 test routines.

---

## 📊 Supported Formats (Compression & Decompression)

`zipper9` delivers enterprise-grade multi-format capability spanning high-speed modern codecs, virtual disk images, and system packages.

### 1. Creation (Compression) Supported Formats

| Format & Standard | Extension | Compression Engine & Core Highlights | Supported Options |
| :--- | :--- | :--- | :--- |
| **ZIP (Zstandard)** | `.zip` | Meta Zstandard native multi-core engine (3-5x faster compression, 5-10x faster decompression than Deflate, **Default**) | Encryption (AES-256), Volume Splitting, Integrity Verification |
| **ZIP (Store)** | `.zip` | Raw uncompressed packaging (Instant multi-gigabyte bundling for pre-compressed videos and photos) | Encryption (AES-256), Volume Splitting, Integrity Verification |
| **7-Zip (LZMA2)** | `.7z` | Native 7-Zip C++ multi-threaded high-ratio compression | Encryption (AES-256), **Header Encryption (Hide filenames)**, Volume Splitting, Integrity Verification |
| **TAR (LZ4 Ultra)** | `.tar.lz4` | RAM-bus bandwidth streaming compression (Tailored for large backups and game assets) | Integrity Verification (`lz4 -t`) |
| **TAR (Gzip)** | `.tar.gz`, `.tgz` | Universal standard tarball distribution across Unix, Linux, and macOS | Encryption, Volume Splitting, Integrity Verification |
| **TAR (XZ)** | `.tar.xz`, `.txz` | Modern Linux kernel and packaging standard (XZ / LZMA2) | Encryption, Volume Splitting, Integrity Verification |
| **TAR (Bzip2)** | `.tar.bz2`, `.tbz2` | Classic Unix high-ratio archive format | Encryption, Volume Splitting, Integrity Verification |
| **TAR (Raw)** | `.tar` | Uncompressed standard POSIX tarball packaging | Encryption, Volume Splitting, Integrity Verification |
| **ISO (UDF 2.60)** | `.iso` | Optical / virtual disk image (UDF 2.60 mastering, 4GB+ large file and Unicode support) | Integrity Verification (`7z t`), Instant OS Mount |

### 2. Extraction (Decompression) Supported Formats (46 Formats)

| Category | Formats | Supported Extensions | Description & Capabilities |
| :--- | :--- | :--- | :--- |
| **Standard Archives** | `ZIP`, `ZIPX`, `7Z`, `RAR`, `RAR5`, `TAR`, `CAB`, `WIM`, `SFX(EXE)` | `.zip`, `.zipx`, `.7z`, `.rar`, `.tar`, `.cab`, `.wim`, `.sfx`, `.sfx.exe` | WinZip high-compression ZIPX, RAR/RAR5, Windows WIM/CAB, Self-Extracting SFX executables |
| **Unix / Linux Packages** | `GZ`, `TGZ`, `BZ`, `BZ2`, `TBZ`, `TBZ2`, `XZ`, `TXZ`, `LZMA`, `TLZ`, `Z`, `TAZ`, `DEB`, `UDEB`, `RPM`, `CPIO`, `ARJ` | `.gz`, `.tgz`, `.bz`, `.bz2`, `.tbz`, `.tbz2`, `.xz`, `.txz`, `.lzma`, `.tlz`, `.z`, `.taz`, `.deb`, `.udeb`, `.rpm`, `.cpio`, `.arj` | Debian/Ubuntu `.deb`, RedHat `.rpm`, legacy Unix `.z`/`.arj`, and raw compression streams |
| **Virtual Disk Images** | `ISO`, `IMG`, `BIN`, `UDF`, `DMG`, `PKG`, `XIP`, `VHD`, `VHDX`, `VMDK`, `VDI`, `QCOW2` | `.iso`, `.img`, `.bin`, `.udf`, `.dmg`, `.pkg`, `.xip`, `.vhd`, `.vhdx`, `.vmdk`, `.vdi`, `.qcow2` | ISO 9660/Joliet/UDF, Apple DMG/PKG, Hyper-V, VMware, VirtualBox, QEMU VM disk image inspection and extraction |
| **Installer / System** | `Compound (MSI, MSP, MSM)`, `NSIS`, `PE` | `.msi`, `.msp`, `.msm`, `.nsis`, `.exe` | Windows Installer packages and Nullsoft installer resource extraction without installation |
| **Legacy Archives** | `LHA`, `LZH`, `ALZ` | `.lha`, `.lzh`, `.alz` | Classic Japanese LHA/LZH and ALZip ALZ (Powered by 100% open-source `unalz`, safe for enterprise use) |
| **Modern Ultra-Fast** | `ZSTD`, `LZ4` | `.zst`, `.tar.zst`, `.lz4`, `.tar.lz4` | Multi-core decompression at memory-bus speeds |
| **❌ Excluded Format** | `EGG` | `.egg` | **Intentionally excluded due to ESTsoft's proprietary restrictive license (commercial redistribution ban)** |

---

## 📦 Multi-Platform Binaries

`zipper9` provides pre-built, ready-to-use binaries tailored for each desktop operating system.  
| Operating System | Package Format | Highlights & Integrations |
| :--- | :--- | :--- |
| **Windows 11 / 10** | `zipper9-windows-x64.exe`<br>`zipper9_shell.msix` | • Portable standalone binary (18MB, no installation required)<br>• Windows 11 modern top-level 1-click context menu (Rust COM DLL)<br>• Windows 10 classic context menu & file association icon binding |
| **Debian / Ubuntu / Raspberry Pi** | `zipper9_1.0.1_amd64.deb`<br>`zipper9_1.0.1_arm64.deb`<br>`zipper9-v1.0.1-linux-*.tar.gz` | • Native 64-bit x86_64 (`amd64`) and ARM64 (`arm64`, Raspberry Pi 4/5, Graviton) support<br>• 1-click `.deb` installation & standalone portable binaries<br>• Seamless integration with system packages (`7zip`, `lz4`, `zstd`)<br>• XDG desktop app launcher & file manager (Nautilus) integration |
| **macOS** | `zipper9-v1.0.1-macos.dmg`<br>`zipper9.app` | • Universal binary for Apple Silicon (M1~M4) & Intel Macs<br>• Standard `/Applications` drag & drop `.dmg` installer<br>• Homebrew Cask standalone recipe (`zipper9.rb`) support |

---

## 📁 Directory Structure

```text
zipper9/
├── requirements.txt            # Python runtime dependencies (CustomTkinter, darkdetect)
├── main.py                     # Application entry point
├── zipper9.rb                  # Standalone Homebrew Cask recipe (macOS)
├── zipper9.spec                # PyInstaller standalone bundling specification
├── run.bat                     # 1-click Windows launch script
├── tools/                      # 100% C/C++ native high-speed engine & shell extension bundles
│   ├── 7z/                     # 7-Zip multi-core engine (7z.exe, 7z.dll)
│   ├── lz4/                    # LZ4 high-throughput engine (lz4.exe)
│   ├── zstd/                   # Zstandard high-ratio engine (zstd.exe)
│   └── modern_shell/           # Windows 11 modern context menu shell extension bundle
├── assets/                     # 3D archive icons (.ico, .png)
├── images/                     # UI screenshots and previews
├── tests/                      # Headless multi-platform CI/CD test suite
└── zipper9_ui/                 # Python modern Fluent GUI
    ├── app.py                  # CustomTkinter main application
    └── bridge/                 # Worker, settings, i18n, and shell extension bridges
```

---

## 🚀 Quick Install & Run

Install and run zipper9 via a single command in your terminal across all supported operating systems.

### 1. Windows 11 / 10
- **WinGet Package Manager**:
  ```powershell
  winget install smin987.zipper9
  ```
- **CLI Terminal Launch (Opens GUI Window)**:
  ```powershell
  zipper9
  # Or open a specific file/folder directly in GUI
  zipper9 sample.zip
  zipper9 C:\data\my_folder
  ```
- **Portable Binary**: Download `zipper9-windows-x64.exe` directly from [GitHub Releases](https://github.com/smin987/zipper9/releases) and double-click to run.

### 2. Debian / Ubuntu / Raspberry Pi
- **APT One-Line Install (amd64)**:
  ```bash
  curl -sLO https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_amd64.deb && sudo apt install -y ./zipper9_1.0.1_amd64.deb && rm zipper9_1.0.1_amd64.deb
  ```
- **APT One-Line Install (arm64 - Raspberry Pi 4/5, Graviton, Apple Silicon Linux VM)**:
  ```bash
  curl -sLO https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_arm64.deb && sudo apt install -y ./zipper9_1.0.1_arm64.deb && rm zipper9_1.0.1_arm64.deb
  ```
- **Portable Binary (.tar.gz)**: Download architecture-specific `zipper9-v1.0.1-linux-*.tar.gz` from [GitHub Releases](https://github.com/smin987/zipper9/releases), extract and run `./zipper9` directly.
- **CLI Terminal Launch (Opens GUI Window)**:
  ```bash
  zipper9
  # Direct argument auto-binding
  zipper9 sample.zip
  zipper9 ./my_project
  ```

### 3. macOS (Apple Silicon & Intel)
- **Homebrew Cask (No separate tap repository required)**:
  ```bash
  brew install --cask https://raw.githubusercontent.com/smin987/zipper9/main/zipper9.rb
  ```
- **CLI Terminal Launch (Opens GUI Window)**:
  ```bash
  zipper9
  # Or standard macOS open command
  open -a zipper9
  ```
- **Direct DMG Installation**: Download `zipper9-v1.0.1-macos.dmg` from [GitHub Releases](https://github.com/smin987/zipper9/releases) and drag `zipper9.app` to `/Applications`.

---

## ❓ FAQ & Troubleshooting

### Q. [Windows] I deleted the portable `zipper9.exe` file directly, but the context menu items still appear.
**A.** This occurs because the shell extension was registered with the modern Windows 11 package and user registry.  
Even if you have already deleted the executable, open **PowerShell** and run the following single-line command to completely clean up all context menu entries and package registrations:

```powershell
Get-AppxPackage *zipper9* | Remove-AppxPackage -ErrorAction SilentlyContinue; Remove-Item -Path "HKCU:\Software\Classes\*\shell\zipper9_compress", "HKCU:\Software\Classes\Directory\shell\zipper9_compress", "HKCU:\Software\Classes\Directory\Background\shell\zipper9_open", "HKCU:\Software\zipper9" -Recurse -Force -ErrorAction SilentlyContinue
```

> *💡 On macOS and Linux, this issue does not occur as the OS automatically cleans up associations upon moving `zipper9.app` to Trash or uninstalling via `apt remove`.*

---

## 💖 Support & Sponsorship

`zipper9` is free software distributed under the **[Source-Available Freeware License](LICENSE)**.  
If you find this project valuable and wish to support its ongoing development and maintenance, consider buying me a coffee! Your support and encouragement are always greatly appreciated. ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/smin987)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/smin987)

</div>

---

## 📄 License

This software is distributed under the **[zipper9 Fair-Code License](LICENSE)** (Source-Available Freeware):
- **Source Code**:
  - **Individuals, Educational & Non-Profit**: Free to inspect, audit, study, and locally modify for personal research or submitting Pull Requests.
  - **Commercial & Enterprise Entities**: Permitted to inspect and audit the Source Code for security review, but **modifying, altering, or creating custom builds of the Source Code is STRICTLY PROHIBITED**. (Commercial entities must use the official free Compiled Binaries.)
  - **All Users**: Modifying the source code to release a competing archiver/compression utility product is strictly prohibited. (Third-party open-source components follow their respective license notices and terms.)
- **Compiled Binaries**: Official executables (`.exe`, `.dmg`, `.deb`, standalone Linux binaries) are **100% Free (Freeware)** for individuals, non-profits, and **commercial/corporate enterprises of any size**.

### Third-Party Open Source Software Notices & Compliance
This software incorporates, bundles, or interfaces with open-source tools including 7-Zip & unRAR (LGPLv2.1+), unalz (zlib/libpng), LZ4 (BSD-2/GPL-2), Zstandard (BSD-3), and CustomTkinter (CC0/MIT).
- **ALZ Format Support**: Powered 100% by the independent open-source engine `unalz` (zlib/libpng License), ensuring zero license audit risk for corporate and enterprise users.
- **EGG Exclusion**: Permanently excluded to eliminate potential copyright disputes stemming from proprietary commercial redistribution restrictions.
- **RAR Compliance**: Read-only decompression via UnRAR; proprietary RAR compression is not implemented.
For complete copyright attributions and full license texts, please refer to **[THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)**.
