# Solar CLI - v1.0.3+ (smart update + pkg manager)
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import importlib.metadata
import urllib.request
from pathlib import Path
import shutil
import zipfile

from .engine import SOLAR_VERSION, run_file


# ---------------- Package Index (YOU EDIT THIS) ----------------
# "checks if theres a variable named the argument after install"
# In Python terms, we do that by looking it up here. If it's not here -> Package not found!
SOLAR_PKG_INDEX: dict[str, dict[str, str]] = {
    # Example package entry you can copy/paste and edit:
    # "examplepkg": {
    #     "url": "https://your-site.com/examplepkg.zip",
    #     "name": "examplepkg",
    #     "version": "1.0.0",
    #     "author": "Dawid",
    #     "description": "Example Solar package",
    #     "homepage": "https://github.com/you/examplepkg",
    # },
}


# ---------------- Updates ----------------
def check_for_updates() -> None:
    try:
        local_version = importlib.metadata.version("solar-lang")
        with urllib.request.urlopen("https://pypi.org/pypi/solar-lang/json", timeout=1.5) as r:
            data = json.load(r)
        latest = data["info"]["version"]
        if local_version != latest:
            print(
                f"[solar] Update available: {local_version} -> {latest}\n"
                f"Run `solar update` to upgrade."
            )
    except Exception:
        # silent fail (offline etc.)
        pass


def _in_venv() -> bool:
    if hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        return True
    if hasattr(sys, "real_prefix"):
        return True
    return False


def _is_linux_or_macos() -> bool:
    return sys.platform.startswith("linux") or sys.platform == "darwin"


def _run_update() -> int:
    cmd = [sys.executable, "-m", "pip", "install", "-U", "solar-lang"]
    if _is_linux_or_macos() and not _in_venv():
        cmd.append("--break-system-packages")
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("Error: pip not found for this Python environment.", file=sys.stderr)
        return 1


# ---------------- Pkg manager paths ----------------
def _solar_home() -> Path:
    return Path.home() / ".solar"


def _packages_dir() -> Path:
    return _solar_home() / "packages"


def _pkg_dest(name: str) -> Path:
    return _packages_dir() / f"pkg-{name}"


# ---------------- Pkg commands ----------------
def _pkg_install(name: str) -> int:
    if name not in SOLAR_PKG_INDEX:
        print("Package not found!")
        return 1

    meta = SOLAR_PKG_INDEX[name]
    url = meta.get("url", "").strip()
    if not url:
        print("Package not found! (missing url)")
        return 1

    dest = _pkg_dest(name)
    if dest.exists():
        print(f"Package already installed: {name}")
        return 1

    # per your request: extract into "pkg-install" in current dir
    workdir = Path.cwd() / "pkg-install"
    if workdir.exists():
        shutil.rmtree(workdir, ignore_errors=True)
    workdir.mkdir(parents=True, exist_ok=True)

    zip_path = workdir / f"{name}.zip"

    try:
        # download
        with urllib.request.urlopen(url, timeout=10) as r:
            zip_path.write_bytes(r.read())
    except Exception as e:
        print(f"Failed to download package: {e}")
        return 1

    # extract
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(workdir)
    except Exception as e:
        print(f"Failed to extract package zip: {e}")
        return 1

    # find main.solar anywhere
    main_file: Path | None = None
    for p in workdir.rglob("main.solar"):
        if p.is_file():
            main_file = p
            break

    if main_file is None:
        print("Package invalid: main.solar not found in zip")
        return 1

    # move folder containing main.solar to ~/.solar/packages/pkg-<name>
    src_dir = main_file.parent

    _packages_dir().mkdir(parents=True, exist_ok=True)

    try:
        # ensure dest parent exists
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.move(str(src_dir), str(dest))
    except Exception as e:
        print(f"Failed to install package: {e}")
        return 1

    # make sure dest has main.solar at its root; if it’s nested, keep as-is but engine will search
    print(f"Package installed: {name}")
    return 0


def _pkg_uninstall(name: str) -> int:
    dest = _pkg_dest(name)
    if not dest.exists():
        print("Package not installed!")
        return 1
    try:
        shutil.rmtree(dest, ignore_errors=True)
        print(f"Package uninstalled: {name}")
        return 0
    except Exception as e:
        print(f"Failed to uninstall package: {e}")
        return 1


def _pkg_info(name: str) -> int:
    if name not in SOLAR_PKG_INDEX:
        print("Package not found!")
        return 1

    meta = SOLAR_PKG_INDEX[name]
    installed = _pkg_dest(name).exists()

    # prints the info based off variables
    print(f"name: {name}")
    print(f"installed: {'yes' if installed else 'no'}")
    for k in ("version", "author", "description", "homepage", "url"):
        if k in meta and meta[k]:
            print(f"{k}: {meta[k]}")
    return 0


# ---------------- Main ----------------
def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(prog="solar", add_help=True)
    sub = ap.add_subparsers(dest="cmd", required=False)

    sub.add_parser("help", help="Show help")

    p_run = sub.add_parser("run", help="Run a .solar file")
    p_run.add_argument("file", help="Path to .solar file")

    sub.add_parser("version", help="Show Solar version")

    sub.add_parser("update", help="Update Solar (pip install -U solar-lang)")

    # solar pkg ...
    p_pkg = sub.add_parser("pkg", help="Solar package manager")
    pkg_sub = p_pkg.add_subparsers(dest="pkgcmd", required=True)

    p_install = pkg_sub.add_parser("install", help="Install a Solar package")
    p_install.add_argument("name", help="Package name")

    p_uninstall = pkg_sub.add_parser("uninstall", help="Uninstall a Solar package")
    p_uninstall.add_argument("name", help="Package name")

    p_info = pkg_sub.add_parser("info", help="Show package info")
    p_info.add_argument("name", help="Package name")

    args = ap.parse_args(argv)

    check_for_updates()

    if args.cmd in (None, "help"):
        ap.print_help()
        return 0

    if args.cmd == "version":
        print(SOLAR_VERSION)
        return 0

    if args.cmd == "run":
        run_file(args.file)
        return 0

    if args.cmd == "update":
        return _run_update()

    if args.cmd == "pkg":
        if args.pkgcmd == "install":
            return _pkg_install(args.name)
        if args.pkgcmd == "uninstall":
            return _pkg_uninstall(args.name)
        if args.pkgcmd == "info":
            return _pkg_info(args.name)
        p_pkg.print_help()
        return 2

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
