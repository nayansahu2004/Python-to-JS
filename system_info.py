import os
import platform
import shutil
import subprocess

# ------------------------- helpers -------------------------


def _run(cmd, timeout=3):
    """Run a command safely. Returns stdout text or ''.
    Accepts either a string (shell) or list (no shell)."""
    try:
        if isinstance(cmd, str):
            return subprocess.check_output(
                cmd, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=timeout
            ).strip()
        else:
            return subprocess.check_output(
                cmd, shell=False, text=True, stderr=subprocess.DEVNULL, timeout=timeout
            ).strip()
    except Exception:
        return ""


def _first_line(s: str) -> str:
    s = (s or "").strip()
    return s.splitlines()[0].strip() if s else ""


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _bool_from_output(s: str) -> bool:
    return s.strip() in {"1", "true", "True", "YES", "Yes", "yes"}


# ------------------------- OS & env -------------------------


def _os_block():
    sysname = platform.system()  # 'Windows', 'Darwin', 'Linux'
    machine = platform.machine() or ""
    release = platform.release() or ""
    version = platform.version() or ""
    kernel = release if sysname == "Windows" else (_run(["uname", "-r"]) or release)

    distro = {"name": "", "version": ""}
    if sysname == "Linux":
        # Best-effort parse of /etc/os-release
        try:
            with open("/etc/os-release", "r") as f:
                data = {}
                for line in f:
                    if "=" in line:
                        k, v = line.rstrip().split("=", 1)
                        data[k] = v.strip('"')
                distro["name"] = data.get("PRETTY_NAME") or data.get("NAME", "")
                distro["version"] = data.get("VERSION_ID") or data.get("VERSION", "")
        except Exception:
            pass

    # WSL / Rosetta detection (harmless if not present)
    wsl = False
    if sysname != "Windows":
        try:
            with open("/proc/version", "r") as f:
                v = f.read().lower()
                wsl = ("microsoft" in v) or ("wsl" in v)
        except Exception:
            wsl = False

    rosetta = False
    if sysname == "Darwin":
        rosetta = _bool_from_output(_run(["sysctl", "-in", "sysctl.proc_translated"]))

    # Target triple (best effort)
    target = ""
    for cc in ("clang", "gcc"):
        if _which(cc):
            out = _run([cc, "-dumpmachine"])
            if out:
                target = _first_line(out)
                break

    return {
        "system": sysname,
        "arch": machine,
        "release": release,
        "version": version,
        "kernel": kernel,
        "distro": distro if sysname == "Linux" else None,
        "wsl": wsl,
        "rosetta2_translated": rosetta,
        "target_triple": target,
    }


# ------------------------- package managers -------------------------


def _package_managers():
    sysname = platform.system()
    pms = []
    if sysname == "Windows":
        for pm in ("winget", "choco", "scoop"):
            if _which(pm):
                pms.append(pm)
    elif sysname == "Darwin":
        if _run(["xcode-select", "-p"]):
            pms.append("xcode-select (CLT)")
        for pm in ("brew", "port"):
            if _which(pm):
                pms.append(pm)
    else:
        for pm in ("apt", "dnf", "yum", "pacman", "zypper", "apk", "emerge"):
            if _which(pm):
                pms.append(pm)
    return pms


# ------------------------- CPU (minimal) -------------------------


def _cpu_block():
    sysname = platform.system()
    brand = ""
    # A simple brand/model read per OS; ignore failures
    if sysname == "Linux":
        brand = _run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    elif sysname == "Darwin":
        brand = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
    elif sysname == "Windows":
        brand = _run('powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).Name"')
        if not brand:
            brand = _run("wmic cpu get Name /value").replace("Name=", "").strip()

    # Logical cores always available; physical is best-effort
    cores_logical = os.cpu_count() or 0
    cores_physical = 0
    if sysname == "Darwin":
        cores_physical = int(_run(["sysctl", "-n", "hw.physicalcpu"]) or "0")
    elif sysname == "Windows":
        cores_physical = int(
            _run('powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).NumberOfCores"')
            or "0"
        )
    elif sysname == "Linux":
        # This is a quick approximation; fine for our use (parallel -j suggestions)
        try:
            # Count unique "core id" per physical id
            mapping = _run("LC_ALL=C lscpu -p=CORE,SOCKET | grep -v '^#'").splitlines()
            unique = set(tuple(line.split(",")) for line in mapping if "," in line)
            cores_physical = len(unique) or 0
        except Exception:
            cores_physical = 0

    # A tiny SIMD hint set (best-effort, optional)
    simd = []
    if sysname == "Linux":
        flags = _run("grep -m1 'flags' /proc/cpuinfo | cut -d: -f2")
        if flags:
            fset = set(flags.upper().split())
            for x in ("AVX512F", "AVX2", "AVX", "FMA", "SSE4_2", "NEON", "SVE"):
                if x in fset:
                    simd.append(x)
    elif sysname == "Darwin":
        feats = (
            (
                _run(["sysctl", "-n", "machdep.cpu.features"])
                + " "
                + _run(["sysctl", "-n", "machdep.cpu.leaf7_features"])
            )
            .upper()
            .split()
        )
        for x in ("AVX512F", "AVX2", "AVX", "FMA", "SSE4_2", "NEON", "SVE"):
            if x in feats:
                simd.append(x)
    # On Windows, skip flags — brand typically suffices for MSVC /arch choice.

    return {
        "brand": brand.strip(),
        "cores_logical": cores_logical,
        "cores_physical": cores_physical,
        "simd": sorted(set(simd)),
    }


# ------------------------- toolchain presence -------------------------


def _toolchain_block():
    def ver_line(exe, args=("--version",)):
        p = _which(exe)
        if not p:
            return ""
        out = _run([p, *args])
        return _first_line(out)

    gcc = ver_line("gcc")
    gpp = ver_line("g++")
    clang = ver_line("clang")

    # MSVC cl (only available inside proper dev shell; handle gracefully)
    msvc_cl = ""
    cl_path = _which("cl")
    if cl_path:
        msvc_cl = _first_line(_run("cl 2>&1"))

    # Build tools (presence + short version line)
    cmake = ver_line("cmake")
    ninja = _first_line(_run([_which("ninja"), "--version"])) if _which("ninja") else ""
    make = ver_line("make")

    # Linker (we only care if lld is available)
    lld = ver_line("ld.lld")
    return {
        "compilers": {"gcc": gcc, "g++": gpp, "clang": clang, "msvc_cl": msvc_cl},
        "build_tools": {"cmake": cmake, "ninja": ninja, "make": make},
        "linkers": {"ld_lld": lld},
    }


# ------------------------- public API -------------------------


def retrieve_system_info():
    """
    Returns a compact dict with enough info for an LLM to:
      - Pick an install path (winget/choco/scoop, Homebrew/Xcode CLT, apt/dnf/...),
      - Choose a compiler family (MSVC/clang/gcc),
      - Suggest safe optimization flags (e.g., -O3/-march=native or MSVC /O2),
      - Decide on a build system (cmake+ninja) and parallel -j value.
    """
    return {
        "os": _os_block(),
        "package_managers": _package_managers(),
        "cpu": _cpu_block(),
        "toolchain": _toolchain_block(),
    }


def rust_toolchain_info():
    """
    Return a dict with JavaScript/Node-related settings:
      - presence and paths for `node`, `npm`, `yarn`, `pnpm`, `nvm`, `npx`
      - versions
      - common env vars (NVM_DIR, NODE_HOME, NPM_CONFIG_PREFIX)
      - simple execution examples
    Works on Windows, macOS, and Linux. Uses the existing helpers: _run, _which, _first_line.
    """
    info = {
        "installed": False,
        "node": {"path": "", "version": ""},
        "npm": {"path": "", "version": ""},
        "yarn": {"path": "", "version": ""},
        "pnpm": {"path": "", "version": ""},
        "nvm": {"path": "", "version": ""},
        "npx": {"path": "", "version": ""},
        "env": {
            "NVM_DIR": os.environ.get("NVM_DIR", ""),
            "NODE_HOME": os.environ.get("NODE_HOME", ""),
            "NPM_CONFIG_PREFIX": os.environ.get("NPM_CONFIG_PREFIX", ""),
        },
        "execution_examples": [],
    }

    # Paths
    node_path = _which("node")
    npm_path = _which("npm")
    yarn_path = _which("yarn")
    pnpm_path = _which("pnpm")
    nvm_path = _which("nvm") or ""
    npx_path = _which("npx")

    info["node"]["path"] = node_path or ""
    info["npm"]["path"] = npm_path or ""
    info["yarn"]["path"] = yarn_path or ""
    info["pnpm"]["path"] = pnpm_path or ""
    info["nvm"]["path"] = nvm_path or ""
    info["npx"]["path"] = npx_path or ""

    # Versions
    if node_path:
        info["node"]["version"] = _first_line(_run([node_path, "--version"]))
    if npm_path:
        info["npm"]["version"] = _first_line(_run([npm_path, "--version"]))
    if yarn_path:
        info["yarn"]["version"] = _first_line(_run([yarn_path, "--version"]))
    if pnpm_path:
        info["pnpm"]["version"] = _first_line(_run([pnpm_path, "--version"]))
    # nvm is a shell function in many installs; try `nvm --version` if available
    if nvm_path:
        info["nvm"]["version"] = _first_line(_run([nvm_path, "--version"]))
    else:
        # Some systems expose NVM_DIR but not an executable
        if os.environ.get("NVM_DIR"):
            info["nvm"]["version"] = "installed (NVM_DIR present)"

    if npx_path:
        info["npx"]["version"] = _first_line(_run([npx_path, "--version"]))

    # Execution examples (only include items that exist on this system)
    exec_examples = []
    if node_path:
        exec_examples.append(f'"{node_path}" index.js')
        exec_examples.append(f'"{node_path}" -v')
    if npm_path:
        exec_examples.append(f'"{npm_path}" install')
        exec_examples.append(f'"{npm_path}" run build')
    if npx_path:
        exec_examples.append(f'"{npx_path}" create-react-app myapp')
    if yarn_path:
        exec_examples.append(f'"{yarn_path}" install')
    if pnpm_path:
        exec_examples.append(f'"{pnpm_path}" install')
    info["execution_examples"] = exec_examples

    # Installed?
    info["installed"] = bool(node_path or npm_path or nvm_path)

    # Normalize common home dirs if env vars missing but typical locations exist
    def _maybe_default_home(env_val, default_basename):
        if env_val:
            return env_val
        home = os.path.expanduser("~") or ""
        candidate = os.path.join(home, default_basename) if home else ""
        return candidate if candidate and os.path.isdir(candidate) else ""

    info["env"]["NVM_DIR"] = _maybe_default_home(info["env"]["NVM_DIR"], ".nvm")
    info["env"]["NODE_HOME"] = _maybe_default_home(info["env"]["NODE_HOME"], ".node")

    return info
