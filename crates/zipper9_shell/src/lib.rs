#![allow(non_snake_case, non_camel_case_types)]

use std::ffi::c_void;
use std::os::windows::ffi::OsStrExt;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicU32, Ordering};

use windows_sys::core::{GUID, HRESULT};
use windows_sys::Win32::Foundation::{BOOL, MAX_PATH, S_FALSE, S_OK, TRUE};
use windows_sys::Win32::System::Com::CoTaskMemAlloc;
use windows_sys::Win32::UI::WindowsAndMessaging::SW_SHOW;

// CLSID: {9999DEAD-9BF7-4CFA-8A5C-DE8679340001}
pub const CLSID_ZIPPER9_COMMAND: GUID = GUID {
    data1: 0x9999DEAD,
    data2: 0x9BF7,
    data3: 0x4CFA,
    data4: [0x8A, 0x5C, 0xDE, 0x86, 0x79, 0x34, 0x00, 0x01],
};

const IID_IUNKNOWN: GUID = GUID {
    data1: 0x00000000,
    data2: 0x0000,
    data3: 0x0000,
    data4: [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46],
};

const IID_ICLASSFACTORY: GUID = GUID {
    data1: 0x00000001,
    data2: 0x0000,
    data3: 0x0000,
    data4: [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46],
};

const IID_IEXPLORERCOMMAND: GUID = GUID {
    data1: 0xa08ce4d0,
    data2: 0xfa25,
    data3: 0x44ab,
    data4: [0xb5, 0x7c, 0xc7, 0xb1, 0xc3, 0x23, 0xe0, 0xb9],
};

const IID_IINITIALIZECOMMAND: GUID = GUID {
    data1: 0x85075acf,
    data2: 0x231f,
    data3: 0x40ea,
    data4: [0x96, 0x10, 0xd2, 0x6b, 0x7b, 0x58, 0xf6, 0x38],
};

const IID_IOBJECTWITHSITE: GUID = GUID {
    data1: 0xfc4801a3,
    data2: 0x2ba9,
    data3: 0x11cf,
    data4: [0xa2, 0x29, 0x00, 0xaa, 0x00, 0x3d, 0x73, 0x52],
};

const SIGDN_FILESYSPATH: u32 = 0x80058000;

const E_NOINTERFACE: HRESULT = -2147467262; // 0x80004002
const E_NOTIMPL: HRESULT = -2147467263; // 0x80004001
const E_POINTER: HRESULT = -2147467261; // 0x80004003
const E_FAIL: HRESULT = -2147467259; // 0x80004005

static OBJECT_COUNT: AtomicU32 = AtomicU32::new(0);

#[inline]
fn log_debug(msg: &str) {
    if let Ok(temp) = std::env::var("TEMP") {
        let path = format!("{}\\zipper9_shell.log", temp);
        use std::io::Write;
        if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
            let _ = writeln!(f, "[PID {}] {}", std::process::id(), msg);
        }
    }
}

fn guid_eq(a: &GUID, b: &GUID) -> bool {
    a.data1 == b.data1 && a.data2 == b.data2 && a.data3 == b.data3 && a.data4 == b.data4
}

// --- vtable 정의 (Windows SDK ShObjIdl_core.h 와 100% 일치) ---
#[repr(C)]
pub struct IClassFactory_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub CreateInstance: unsafe extern "system" fn(*mut c_void, *mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub LockServer: unsafe extern "system" fn(*mut c_void, BOOL) -> HRESULT,
}

#[repr(C)]
pub struct IExplorerCommand_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub GetTitle: unsafe extern "system" fn(*mut c_void, *mut c_void, *mut *mut u16) -> HRESULT,
    pub GetIcon: unsafe extern "system" fn(*mut c_void, *mut c_void, *mut *mut u16) -> HRESULT,
    pub GetToolTip: unsafe extern "system" fn(*mut c_void, *mut c_void, *mut *mut u16) -> HRESULT,
    pub GetCanonicalName: unsafe extern "system" fn(*mut c_void, *mut GUID) -> HRESULT,
    pub GetState: unsafe extern "system" fn(*mut c_void, *mut c_void, BOOL, *mut u32) -> HRESULT,
    pub Invoke: unsafe extern "system" fn(*mut c_void, *mut c_void, *mut c_void) -> HRESULT,
    pub GetFlags: unsafe extern "system" fn(*mut c_void, *mut u32) -> HRESULT,
    pub EnumSubCommands: unsafe extern "system" fn(*mut c_void, *mut *mut c_void) -> HRESULT,
}

#[repr(C)]
pub struct IInitializeCommand_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Initialize: unsafe extern "system" fn(*mut c_void, *const u16, *mut c_void) -> HRESULT,
}

#[repr(C)]
pub struct IObjectWithSite_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub SetSite: unsafe extern "system" fn(*mut c_void, *mut c_void) -> HRESULT,
    pub GetSite: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
}

#[repr(C)]
pub struct IShellItemArray_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub BindToHandler: unsafe extern "system" fn(*mut c_void, *mut c_void, *const GUID, *const GUID, *mut *mut c_void) -> HRESULT,
    pub GetPropertyStore: unsafe extern "system" fn(*mut c_void, u32, *const GUID, *mut *mut c_void) -> HRESULT,
    pub GetPropertyDescriptionList: unsafe extern "system" fn(*mut c_void, *const c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub GetAttributes: unsafe extern "system" fn(*mut c_void, u32, u32, *mut u32) -> HRESULT,
    pub GetCount: unsafe extern "system" fn(*mut c_void, *mut u32) -> HRESULT,
    pub GetItemAt: unsafe extern "system" fn(*mut c_void, u32, *mut *mut c_void) -> HRESULT,
}

#[repr(C)]
pub struct IShellItem_Vtbl {
    pub QueryInterface: unsafe extern "system" fn(*mut c_void, *const GUID, *mut *mut c_void) -> HRESULT,
    pub AddRef: unsafe extern "system" fn(*mut c_void) -> u32,
    pub Release: unsafe extern "system" fn(*mut c_void) -> u32,
    pub BindToHandler: unsafe extern "system" fn(*mut c_void, *mut c_void, *const GUID, *const GUID, *mut *mut c_void) -> HRESULT,
    pub GetParent: unsafe extern "system" fn(*mut c_void, *mut *mut c_void) -> HRESULT,
    pub GetDisplayName: unsafe extern "system" fn(*mut c_void, u32, *mut *mut u16) -> HRESULT,
}

// --- 헬퍼 함수 ---
fn to_wide(s: &str) -> Vec<u16> {
    std::ffi::OsStr::new(s).encode_wide().chain(Some(0)).collect()
}

fn alloc_cotask_str(s: &str) -> *mut u16 {
    let wide = to_wide(s);
    unsafe {
        let ptr = CoTaskMemAlloc(wide.len() * 2) as *mut u16;
        if !ptr.is_null() {
            std::ptr::copy_nonoverlapping(wide.as_ptr(), ptr, wide.len());
        }
        ptr
    }
}

fn is_archive_file(path_str: &str) -> bool {
    let lower = path_str.to_lowercase();
    let exts = [
        ".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".bz2", ".xz",
        ".lz4", ".zst", ".iso", ".cab", ".wim", ".alz", ".egg", ".001",
    ];
    exts.iter().any(|ext| lower.ends_with(ext))
}

fn get_first_item_path(psiItemArray: *mut c_void) -> Option<PathBuf> {
    get_all_item_paths(psiItemArray).into_iter().next()
}

fn get_all_item_paths(psiItemArray: *mut c_void) -> Vec<PathBuf> {
    let mut paths = Vec::new();
    if psiItemArray.is_null() {
        return paths;
    }
    unsafe {
        let vtbl_ptr = *(psiItemArray as *const *const IShellItemArray_Vtbl);
        if vtbl_ptr.is_null() {
            return paths;
        }
        let mut count: u32 = 0;
        let hr_count = ((*vtbl_ptr).GetCount)(psiItemArray, &mut count);
        if hr_count != S_OK || count == 0 {
            return paths;
        }

        for i in 0..count {
            let mut item: *mut c_void = std::ptr::null_mut();
            let hr_item = ((*vtbl_ptr).GetItemAt)(psiItemArray, i, &mut item);
            if hr_item == S_OK && !item.is_null() {
                let item_vtbl = *(item as *const *const IShellItem_Vtbl);
                if !item_vtbl.is_null() {
                    let mut name_ptr: *mut u16 = std::ptr::null_mut();
                    let res = ((*item_vtbl).GetDisplayName)(item, SIGDN_FILESYSPATH, &mut name_ptr);
                    ((*item_vtbl).Release)(item);

                    if res == S_OK && !name_ptr.is_null() {
                        let mut len = 0;
                        while *name_ptr.add(len) != 0 {
                            len += 1;
                        }
                        let slice = std::slice::from_raw_parts(name_ptr, len);
                        use std::os::windows::ffi::OsStringExt;
                        let os_str = std::ffi::OsString::from_wide(slice);
                        windows_sys::Win32::System::Com::CoTaskMemFree(name_ptr as *mut _);
                        paths.push(PathBuf::from(os_str));
                    }
                } else {
                    ((*item_vtbl).Release)(item);
                }
            }
        }
    }
    paths
}

fn find_zipper9_exe() -> Option<PathBuf> {
    // 1. 레지스트리 HKCU\Software\zipper9 -> ExePath
    use windows_sys::Win32::System::Registry::{RegCloseKey, RegOpenKeyExW, RegQueryValueExW, HKEY_CURRENT_USER, KEY_READ, REG_SZ};
    let subkey = to_wide(r"Software\zipper9");
    let val_name = to_wide("ExePath");
    let mut hkey = std::ptr::null_mut();
    unsafe {
        if RegOpenKeyExW(HKEY_CURRENT_USER, subkey.as_ptr(), 0, KEY_READ, &mut hkey) == 0 {
            let mut buf = [0u16; MAX_PATH as usize];
            let mut cb = (MAX_PATH * 2) as u32;
            let mut val_type = 0u32;
            let res = RegQueryValueExW(hkey, val_name.as_ptr(), std::ptr::null_mut(), &mut val_type, buf.as_mut_ptr() as *mut _, &mut cb);
            RegCloseKey(hkey);
            if res == 0 && (val_type == REG_SZ || val_type == 2) {
                let len = (cb / 2) as usize;
                let actual_len = buf[..len].iter().position(|&c| c == 0).unwrap_or(len);
                use std::os::windows::ffi::OsStringExt;
                let p = PathBuf::from(std::ffi::OsString::from_wide(&buf[..actual_len]));
                if p.is_file() {
                    return Some(p);
                }
            }
        }
    }

    // 2. 개발 및 배포 루트 dist/zipper9.exe
    let cand_dist = PathBuf::from(r"D:\mirror\dev\MyPython\in_service\zipper9\dist\zipper9.exe");
    if cand_dist.is_file() {
        return Some(cand_dist);
    }

    // 3. AppData 설치 경로
    if let Ok(local_appdata) = std::env::var("LOCALAPPDATA") {
        let p = PathBuf::from(local_appdata).join(r"Programs\zipper9\zipper9.exe");
        if p.is_file() {
            return Some(p);
        }
    }

    // 4. Program Files 설치 경로
    if let Ok(prog_files) = std::env::var("ProgramFiles") {
        let p = PathBuf::from(prog_files).join(r"zipper9\zipper9.exe");
        if p.is_file() {
            return Some(p);
        }
    }

    None
}

// --- COM 개체 구현체 ---
#[repr(C)]
struct Zipper9Command {
    vtbl_cmd: *const IExplorerCommand_Vtbl,
    vtbl_init: *const IInitializeCommand_Vtbl,
    vtbl_site: *const IObjectWithSite_Vtbl,
    ref_count: AtomicU32,
    is_background: AtomicBool,
    is_open_mode: AtomicBool,
}

static COMMAND_VTBL: IExplorerCommand_Vtbl = IExplorerCommand_Vtbl {
    QueryInterface: Command_QueryInterface,
    AddRef: Command_AddRef,
    Release: Command_Release,
    GetTitle: Command_GetTitle,
    GetIcon: Command_GetIcon,
    GetToolTip: Command_GetToolTip,
    GetCanonicalName: Command_GetCanonicalName,
    GetState: Command_GetState,
    Invoke: Command_Invoke,
    GetFlags: Command_GetFlags,
    EnumSubCommands: Command_EnumSubCommands,
};

static INIT_VTBL: IInitializeCommand_Vtbl = IInitializeCommand_Vtbl {
    QueryInterface: Init_QueryInterface,
    AddRef: Init_AddRef,
    Release: Init_Release,
    Initialize: Init_Initialize,
};

static SITE_VTBL: IObjectWithSite_Vtbl = IObjectWithSite_Vtbl {
    QueryInterface: Site_QueryInterface,
    AddRef: Site_AddRef,
    Release: Site_Release,
    SetSite: Site_SetSite,
    GetSite: Site_GetSite,
};

fn query_interface_impl(this: *mut Zipper9Command, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    if ppv.is_null() || riid.is_null() {
        return E_POINTER;
    }
    let guid = unsafe { *riid };
    log_debug(&format!("QI requested: {:08x}-{:04x}-{:04x}-{:02x}{:02x}-{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}",
        guid.data1, guid.data2, guid.data3,
        guid.data4[0], guid.data4[1], guid.data4[2], guid.data4[3],
        guid.data4[4], guid.data4[5], guid.data4[6], guid.data4[7]
    ));
    unsafe {
        if guid_eq(&guid, &IID_IUNKNOWN) || guid_eq(&guid, &IID_IEXPLORERCOMMAND) {
            log_debug("QI: Handled IUnknown / IExplorerCommand -> S_OK");
            Command_AddRef(this as *mut c_void);
            *ppv = this as *mut c_void;
            return S_OK;
        }
        if guid_eq(&guid, &IID_IINITIALIZECOMMAND) {
            log_debug("QI: Handled IInitializeCommand -> S_OK");
            Command_AddRef(this as *mut c_void);
            *ppv = (this as *mut u8).add(std::mem::size_of::<usize>()) as *mut c_void;
            return S_OK;
        }
        if guid_eq(&guid, &IID_IOBJECTWITHSITE) {
            log_debug("QI: Handled IObjectWithSite -> S_OK");
            Command_AddRef(this as *mut c_void);
            *ppv = (this as *mut u8).add(2 * std::mem::size_of::<usize>()) as *mut c_void;
            return S_OK;
        }
        *ppv = std::ptr::null_mut();
    }
    log_debug("QI: Unsupported interface -> E_NOINTERFACE");
    E_NOINTERFACE
}

// --- IExplorerCommand 메서드 ---
unsafe extern "system" fn Command_QueryInterface(this: *mut c_void, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    query_interface_impl(this as *mut Zipper9Command, riid, ppv)
}

unsafe extern "system" fn Command_AddRef(this: *mut c_void) -> u32 {
    let cmd = &*(this as *const Zipper9Command);
    cmd.ref_count.fetch_add(1, Ordering::SeqCst) + 1
}

unsafe extern "system" fn Command_Release(this: *mut c_void) -> u32 {
    let cmd = &*(this as *const Zipper9Command);
    let prev = cmd.ref_count.fetch_sub(1, Ordering::SeqCst);
    if prev == 1 {
        OBJECT_COUNT.fetch_sub(1, Ordering::SeqCst);
        let _ = Box::from_raw(this as *mut Zipper9Command);
        return 0;
    }
    prev - 1
}

unsafe extern "system" fn Command_GetTitle(
    this: *mut c_void,
    psiItemArray: *mut c_void,
    ppszName: *mut *mut u16,
) -> HRESULT {
    if ppszName.is_null() {
        return E_POINTER;
    }
    let cmd = &*(this as *const Zipper9Command);
    let is_bg = cmd.is_background.load(Ordering::SeqCst);
    let first_item = get_first_item_path(psiItemArray);
    log_debug(&format!("Command_GetTitle: is_bg={}, first_item={:?}", is_bg, first_item));

    let is_desktop_dir = if let Some(ref path) = first_item {
        let s = path.to_string_lossy().to_lowercase();
        s.ends_with(r"\desktop") || s.ends_with(r"\바탕 화면") || s.ends_with(r"\바탕화면")
    } else {
        false
    };

    let title = if is_bg || is_desktop_dir {
        cmd.is_open_mode.store(true, Ordering::SeqCst);
        "⚡ zipper9 열기"
    } else if let Some(ref path) = first_item {
        if path.is_file() && is_archive_file(&path.to_string_lossy()) {
            cmd.is_open_mode.store(false, Ordering::SeqCst);
            "⚡ zipper9으로 풀기"
        } else {
            cmd.is_open_mode.store(false, Ordering::SeqCst);
            "⚡ zipper9으로 압축하기"
        }
    } else {
        // 바탕화면 또는 폴더 빈 공간 등 선택 항목이 없을 때
        cmd.is_open_mode.store(true, Ordering::SeqCst);
        "⚡ zipper9 열기"
    };

    log_debug(&format!("Command_GetTitle title decided: '{}'", title));

    let ptr = alloc_cotask_str(title);
    if ptr.is_null() {
        E_POINTER
    } else {
        *ppszName = ptr;
        S_OK
    }
}

unsafe extern "system" fn Command_GetIcon(
    _this: *mut c_void,
    _psiItemArray: *mut c_void,
    ppszIcon: *mut *mut u16,
) -> HRESULT {
    log_debug("Command_GetIcon called");
    if ppszIcon.is_null() {
        return E_POINTER;
    }
    *ppszIcon = std::ptr::null_mut();

    if let Some(exe_path) = find_zipper9_exe() {
        let icon_spec = format!("{},0", exe_path.to_string_lossy());
        let ptr = alloc_cotask_str(&icon_spec);
        if !ptr.is_null() {
            *ppszIcon = ptr;
            log_debug(&format!("Command_GetIcon returning icon: {}", icon_spec));
            return S_OK;
        }
    }

    // 아이콘이 없거나 실패 시 절대 S_FALSE를 반환하지 않는다!
    // S_FALSE는 SUCCEEDED()로 판정되어 Windows.UI.FileExplorer.dll이 null 포인터를 참조해 0xc0000005 크래시 발생!
    E_NOTIMPL
}

unsafe extern "system" fn Command_GetToolTip(_this: *mut c_void, _psi: *mut c_void, ppszToolTip: *mut *mut u16) -> HRESULT {
    if ppszToolTip.is_null() {
        return E_POINTER;
    }
    *ppszToolTip = std::ptr::null_mut();
    E_NOTIMPL
}

unsafe extern "system" fn Command_GetCanonicalName(_this: *mut c_void, pguidCommandName: *mut GUID) -> HRESULT {
    log_debug("Command_GetCanonicalName called");
    if pguidCommandName.is_null() {
        return E_POINTER;
    }
    *pguidCommandName = CLSID_ZIPPER9_COMMAND;
    S_OK
}

unsafe extern "system" fn Command_GetState(_this: *mut c_void, _psi: *mut c_void, _fOkToBeSlow: BOOL, pCmdState: *mut u32) -> HRESULT {
    log_debug("Command_GetState called");
    if pCmdState.is_null() {
        return E_POINTER;
    }
    *pCmdState = 0; // ECS_ENABLED
    S_OK
}

unsafe extern "system" fn Command_Invoke(
    this: *mut c_void,
    psiItemArray: *mut c_void,
    _pbc: *mut c_void,
) -> HRESULT {
    log_debug("Command_Invoke called");
    let cmd = &*(this as *const Zipper9Command);
    let is_bg = cmd.is_background.load(Ordering::SeqCst);
    let is_open_mode = cmd.is_open_mode.load(Ordering::SeqCst);

    let Some(exe_path) = find_zipper9_exe() else {
        log_debug("find_zipper9_exe returned None!");
        return S_FALSE;
    };
    log_debug(&format!("Found zipper9 exe: {}", exe_path.display()));

    let items = get_all_item_paths(psiItemArray);
    log_debug(&format!("Invoke items count: {}, is_bg={}, is_open_mode={}", items.len(), is_bg, is_open_mode));
    for (i, it) in items.iter().enumerate() {
        log_debug(&format!("  item[{}]: {}", i, it.display()));
    }

    // 1. 열기 모드 (바탕화면/폴더 빈공간 우클릭, 선택 항목 없음, 또는 사용자가 'zipper9 열기' 메뉴를 누른 경우)
    if is_bg || is_open_mode || items.is_empty() {
        log_debug("Spawning zipper9 standalone GUI (open mode)...");

        // 1순위: std::process::Command (가장 신뢰성 높은 Win32 자식 프로세스 스폰)
        let mut proc_cmd = std::process::Command::new(&exe_path);
        if let Some(parent) = exe_path.parent() {
            proc_cmd.current_dir(parent);
        }
        match proc_cmd.spawn() {
            Ok(child) => {
                log_debug(&format!("Spawned via std::process::Command: PID {}", child.id()));
                return S_OK;
            }
            Err(e) => {
                log_debug(&format!("std::process::Command failed: {}, falling back to ShellExecuteW", e));
            }
        }

        // 2순위: ShellExecuteW 폴백
        let exe_wide = to_wide(&exe_path.to_string_lossy());
        let parent_wide = exe_path.parent().map(|p| to_wide(&p.to_string_lossy()));
        let dir_ptr = parent_wide.as_ref().map(|w| w.as_ptr()).unwrap_or(std::ptr::null());

        use windows_sys::Win32::UI::Shell::ShellExecuteW;
        let res = ShellExecuteW(
            std::ptr::null_mut(),
            to_wide("open").as_ptr(),
            exe_wide.as_ptr(),
            std::ptr::null(),
            dir_ptr,
            SW_SHOW,
        );
        log_debug(&format!("ShellExecuteW standalone result: {}", res as usize));
        return if (res as usize) > 32 { S_OK } else { S_FALSE };
    }

    // 2. 파일/폴더 선택 압축 또는 해제 모드
    let first = &items[0];
    let is_single_archive = items.len() == 1 && first.is_file() && is_archive_file(&first.to_string_lossy());
    let flag = if is_single_archive { "--extract-instant" } else { "--compress-instant" };

    log_debug(&format!("Executing with flag: {} for {} items", flag, items.len()));

    // 1순위: std::process::Command
    let mut proc_cmd = std::process::Command::new(&exe_path);
    proc_cmd.arg(flag);
    for item in &items {
        proc_cmd.arg(item);
    }
    if let Some(parent) = exe_path.parent() {
        proc_cmd.current_dir(parent);
    }
    match proc_cmd.spawn() {
        Ok(child) => {
            log_debug(&format!("Spawned via std::process::Command with args: PID {}", child.id()));
            return S_OK;
        }
        Err(e) => {
            log_debug(&format!("std::process::Command with args failed: {}, falling back to ShellExecuteW", e));
        }
    }

    // 2순위: ShellExecuteW
    let mut params_str = flag.to_string();
    for item in items {
        params_str.push_str(&format!(" \"{}\"", item.to_string_lossy()));
    }
    let exe_wide = to_wide(&exe_path.to_string_lossy());
    let params_wide = to_wide(&params_str);
    let parent_wide = exe_path.parent().map(|p| to_wide(&p.to_string_lossy()));
    let dir_ptr = parent_wide.as_ref().map(|w| w.as_ptr()).unwrap_or(std::ptr::null());

    use windows_sys::Win32::UI::Shell::ShellExecuteW;
    let res = ShellExecuteW(
        std::ptr::null_mut(),
        to_wide("open").as_ptr(),
        exe_wide.as_ptr(),
        params_wide.as_ptr(),
        dir_ptr,
        SW_SHOW,
    );
    log_debug(&format!("ShellExecuteW with args result: {}", res as usize));

    S_OK
}

unsafe extern "system" fn Command_GetFlags(_this: *mut c_void, pFlags: *mut u32) -> HRESULT {
    log_debug("Command_GetFlags called");
    if pFlags.is_null() {
        return E_POINTER;
    }
    *pFlags = 0; // ECF_DEFAULT
    S_OK
}

unsafe extern "system" fn Command_EnumSubCommands(_this: *mut c_void, ppEnum: *mut *mut c_void) -> HRESULT {
    log_debug("Command_EnumSubCommands called");
    if ppEnum.is_null() {
        return E_POINTER;
    }
    *ppEnum = std::ptr::null_mut();
    E_NOTIMPL
}

// --- IInitializeCommand 메서드 ---
unsafe extern "system" fn Init_QueryInterface(this: *mut c_void, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    let base = (this as *mut u8).sub(std::mem::size_of::<usize>()) as *mut Zipper9Command;
    query_interface_impl(base, riid, ppv)
}

unsafe extern "system" fn Init_AddRef(this: *mut c_void) -> u32 {
    let base = (this as *mut u8).sub(std::mem::size_of::<usize>()) as *mut c_void;
    Command_AddRef(base)
}

unsafe extern "system" fn Init_Release(this: *mut c_void) -> u32 {
    let base = (this as *mut u8).sub(std::mem::size_of::<usize>()) as *mut c_void;
    Command_Release(base)
}

unsafe extern "system" fn Init_Initialize(this: *mut c_void, pszCommandName: *const u16, _ppb: *mut c_void) -> HRESULT {
    let base = (this as *mut u8).sub(std::mem::size_of::<usize>()) as *mut Zipper9Command;
    if !pszCommandName.is_null() {
        let mut len = 0;
        while *pszCommandName.add(len) != 0 {
            len += 1;
        }
        let slice = std::slice::from_raw_parts(pszCommandName, len);
        use std::os::windows::ffi::OsStringExt;
        let verb = std::ffi::OsString::from_wide(slice);
        if let Some(verb_str) = verb.to_str() {
            log_debug(&format!("Init_Initialize verb: '{}'", verb_str));
            if verb_str.contains("Background") {
                (*base).is_background.store(true, Ordering::SeqCst);
                (*base).is_open_mode.store(true, Ordering::SeqCst);
            }
        }
    } else {
        log_debug("Init_Initialize called with null verb");
    }
    S_OK
}

// --- IObjectWithSite 메서드 ---
unsafe extern "system" fn Site_QueryInterface(this: *mut c_void, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    let base = (this as *mut u8).sub(2 * std::mem::size_of::<usize>()) as *mut Zipper9Command;
    query_interface_impl(base, riid, ppv)
}

unsafe extern "system" fn Site_AddRef(this: *mut c_void) -> u32 {
    let base = (this as *mut u8).sub(2 * std::mem::size_of::<usize>()) as *mut c_void;
    Command_AddRef(base)
}

unsafe extern "system" fn Site_Release(this: *mut c_void) -> u32 {
    let base = (this as *mut u8).sub(2 * std::mem::size_of::<usize>()) as *mut c_void;
    Command_Release(base)
}

unsafe extern "system" fn Site_SetSite(_this: *mut c_void, _pUnkSite: *mut c_void) -> HRESULT {
    log_debug("Site_SetSite called");
    S_OK
}

unsafe extern "system" fn Site_GetSite(_this: *mut c_void, _riid: *const GUID, ppvSite: *mut *mut c_void) -> HRESULT {
    if ppvSite.is_null() {
        return E_POINTER;
    }
    *ppvSite = std::ptr::null_mut();
    E_FAIL
}

// --- IClassFactory 구현체 ---
#[repr(C)]
struct ClassFactory {
    lpVtbl: *const IClassFactory_Vtbl,
    ref_count: AtomicU32,
}

static FACTORY_VTBL: IClassFactory_Vtbl = IClassFactory_Vtbl {
    QueryInterface: Factory_QueryInterface,
    AddRef: Factory_AddRef,
    Release: Factory_Release,
    CreateInstance: Factory_CreateInstance,
    LockServer: Factory_LockServer,
};

unsafe extern "system" fn Factory_QueryInterface(this: *mut c_void, riid: *const GUID, ppv: *mut *mut c_void) -> HRESULT {
    if ppv.is_null() || riid.is_null() {
        return E_POINTER;
    }
    let guid = *riid;
    if guid_eq(&guid, &IID_IUNKNOWN) || guid_eq(&guid, &IID_ICLASSFACTORY) {
        Factory_AddRef(this);
        *ppv = this;
        return S_OK;
    }
    *ppv = std::ptr::null_mut();
    E_NOINTERFACE
}

unsafe extern "system" fn Factory_AddRef(this: *mut c_void) -> u32 {
    let f = &*(this as *const ClassFactory);
    f.ref_count.fetch_add(1, Ordering::SeqCst) + 1
}

unsafe extern "system" fn Factory_Release(this: *mut c_void) -> u32 {
    let f = &*(this as *const ClassFactory);
    let prev = f.ref_count.fetch_sub(1, Ordering::SeqCst);
    if prev == 1 {
        OBJECT_COUNT.fetch_sub(1, Ordering::SeqCst);
        let _ = Box::from_raw(this as *mut ClassFactory);
        return 0;
    }
    prev - 1
}

unsafe extern "system" fn Factory_CreateInstance(
    _this: *mut c_void,
    pUnkOuter: *mut c_void,
    riid: *const GUID,
    ppvObject: *mut *mut c_void,
) -> HRESULT {
    log_debug("Factory_CreateInstance called");
    if !pUnkOuter.is_null() {
        return -2147221232; // CLASS_E_NOAGGREGATION
    }
    if ppvObject.is_null() || riid.is_null() {
        return E_POINTER;
    }

    let cmd = Box::into_raw(Box::new(Zipper9Command {
        vtbl_cmd: &COMMAND_VTBL,
        vtbl_init: &INIT_VTBL,
        vtbl_site: &SITE_VTBL,
        ref_count: AtomicU32::new(1),
        is_background: AtomicBool::new(false),
        is_open_mode: AtomicBool::new(false),
    }));
    OBJECT_COUNT.fetch_add(1, Ordering::SeqCst);

    let hr = query_interface_impl(cmd, riid, ppvObject);
    Command_Release(cmd as *mut c_void);
    hr
}

unsafe extern "system" fn Factory_LockServer(_this: *mut c_void, fLock: BOOL) -> HRESULT {
    if fLock == TRUE {
        OBJECT_COUNT.fetch_add(1, Ordering::SeqCst);
    } else {
        OBJECT_COUNT.fetch_sub(1, Ordering::SeqCst);
    }
    S_OK
}

// --- DLL Exports ---
#[no_mangle]
pub unsafe extern "system" fn DllGetClassObject(
    rclsid: *const GUID,
    riid: *const GUID,
    ppv: *mut *mut c_void,
) -> HRESULT {
    log_debug("DllGetClassObject called");
    if rclsid.is_null() || riid.is_null() || ppv.is_null() {
        return E_POINTER;
    }
    if !guid_eq(&*rclsid, &CLSID_ZIPPER9_COMMAND) {
        *ppv = std::ptr::null_mut();
        return -2147221231; // CLASS_E_CLASSNOTAVAILABLE
    }

    let factory = Box::into_raw(Box::new(ClassFactory {
        lpVtbl: &FACTORY_VTBL,
        ref_count: AtomicU32::new(1),
    }));
    OBJECT_COUNT.fetch_add(1, Ordering::SeqCst);

    let hr = Factory_QueryInterface(factory as *mut c_void, riid, ppv);
    Factory_Release(factory as *mut c_void);
    hr
}

#[no_mangle]
pub unsafe extern "system" fn DllCanUnloadNow() -> HRESULT {
    if OBJECT_COUNT.load(Ordering::SeqCst) == 0 {
        S_OK
    } else {
        S_FALSE
    }
}
