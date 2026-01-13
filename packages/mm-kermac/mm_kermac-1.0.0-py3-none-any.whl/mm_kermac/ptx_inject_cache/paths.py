# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

from platformdirs import user_cache_dir
import sys
from importlib.resources import files
from pathlib import Path
from importlib.metadata import version
import hashlib 
import uuid
import json
import tempfile
import cuda.pathfinder
import mm_ptx

def get_package_name():
    return "mm_kermac"

def get_package_version():
    try:
        pkg_version = version(get_package_name())
        return pkg_version
    except Exception as e:
        return f"Could not determine version: {e}"

def get_top_level_repo_dir(dir) -> Path:
    # directory *beside* the package (wheel layout)
    wheel_copy = files(get_package_name()).parent / dir
    # directory *beside* src/ (editable / repo checkout)
    repo_copy  = Path(__file__).resolve().parents[3] / dir

    for path in (repo_copy, wheel_copy):
        if path.is_dir():
            return path.resolve()

    raise FileNotFoundError("top level directory not found")

def get_include_local_cuda_dir() -> Path:
    return get_top_level_repo_dir('include')

def get_local_cuda_kernel_dir() -> Path:
    return get_top_level_repo_dir('kernels')

def get_include_paths():
    return [
        cuda.pathfinder.find_nvidia_header_directory('cccl'),       # for cstdint, etc..
        cuda.pathfinder.find_nvidia_header_directory('nvrtc'),      # for cuda_runtime_api.
        cuda.pathfinder.find_nvidia_header_directory('cudart'),
        get_include_local_cuda_dir(),                               # for common includes
        mm_ptx.get_include_dir(),                                   # for ptx_inject.h (+ bundled boost)
        get_top_level_repo_dir('thirdparty/cutlass/include'),   # for cutlass includes
    ]

def cache_root() -> Path:
    """
    <user_cache_dir>/<your-package>/<env-id>/
    Guaranteed unique per virtual-env *and* persistent across runs.
    """
    try:
        # 1. A stable ID for THIS Python installation / venv
        env_id = hashlib.sha256(sys.prefix.encode()).hexdigest()[:12]

        # 2. RFC 6685 cache location that respects XDG / Windows / macOS rules
        base_dir = Path(user_cache_dir(f'{get_package_name()}')) / f'{get_package_version()}'
    
        # 3. Create sub-dir and a sentinel file on first use
        target = base_dir / env_id
        target.mkdir(parents=True, exist_ok=True)

        sentinel = target / "instance.json"
        if not sentinel.exists():
            sentinel.write_text(json.dumps({"uuid": str(uuid.uuid4())}))
        return target
    except Exception:               # Fallback: tmpdir
        return Path(tempfile.mkdtemp(prefix=f'{get_package_name()}-cache-'))
