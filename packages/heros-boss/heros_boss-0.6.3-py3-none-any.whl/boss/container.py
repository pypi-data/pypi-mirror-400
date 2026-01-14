"""Includes utilities to handle BOSS starting in a container."""

from pathlib import Path
import json
import os
import sys
import subprocess


def is_in_container():
    """Checks if the current process is running inside a docker or podman container."""
    cgroup = Path("/proc/self/cgroup")
    return (
        Path("/.dockerenv").is_file()  # docker
        or (cgroup.is_file() and "docker" in cgroup.read_text())  # docker
        or Path("/run/.containerenv").is_file()  # podman
        or Path("/var/run/.containerenv").is_file()  # podman (FreeBSD)
    )


def prepare_container():
    """Installs extra packages to the docker container."""

    require_restart = False
    pkg_file = Path("/var/lib/boss/installed_pkgs.json")
    local_pkgs_path = Path("/etc/boss/")
    if pkg_file.is_file():
        with pkg_file.open("rb") as f:
            installed_pkgs = json.load(f)
    else:
        installed_pkgs = {"pip": [], "local": {}, "apt": []}

    if (apt_pkgs := os.environ.get("BOSS_APT_PKGS")) is not None:
        missing_pkgs = []
        for pkg in apt_pkgs.replace(" ", ",").split(","):
            if pkg not in installed_pkgs["apt"]:
                installed_pkgs["apt"].append(pkg)
                missing_pkgs.append(pkg)
                require_restart = True
        if missing_pkgs:
            subprocess.check_call(["apt-get", "update"])
            subprocess.check_call(["apt-get", "install", "-y"] + missing_pkgs)

    if (pip_pkgs := os.environ.get("BOSS_PIP_PKGS")) is not None:
        for pkg in pip_pkgs.replace(" ", ",").split(","):
            if pkg not in installed_pkgs["pip"]:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                installed_pkgs["pip"].append(pkg)
                require_restart = True

    if local_pkgs_path.is_dir():
        for script in local_pkgs_path.rglob("*.boss.sh"):
            if script.stem not in installed_pkgs["local"]:
                subprocess.check_call(["/bin/bash", str(script)])
                installed_pkgs["local"][script.stem] = str(script)
                require_restart = True

    if require_restart:
        pkg_file.parent.mkdir(parents=True, exist_ok=True)
        with pkg_file.open("w") as f:
            json.dump(installed_pkgs, f)

    return require_restart
