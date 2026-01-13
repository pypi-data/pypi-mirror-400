# SPDX-FileCopyrightText: 2026 MetaMachines LLC
#
# SPDX-License-Identifier: MIT

import threading
from typing import Any
import sys
import torch
import sqlite3
import os
import hashlib

from cuda.core import Device, Program, ProgramOptions

from .function_db_key import *
from .function_db_value import *

from .paths import *

def get_compute_capability(device) -> str:
    if isinstance(device, torch.device):
        pt_device_id = device.index
        device = Device(pt_device_id)
    
    arch = "".join(f"{i}" for i in device.compute_capability)
    return arch

def hash_cuda_include_files(directories):
    # Initialize SHA-256 hash object
    hasher = hashlib.sha256()
    
    for directory in directories:
        # Walk through the directory
        for root, _, files in os.walk(directory):
            # Sort files for consistent hash across runs
            for file_name in sorted(files):
                # Check if file is a text file (e.g., ends with .cuh)
                if file_name.endswith('.cuh'):
                    file_path = os.path.join(root, file_name)
                    try:
                        # Read file in binary mode
                        with open(file_path, 'rb') as f:
                            # Update hash with file contents
                            while chunk := f.read(8192): # Read in 8KB chunks
                                hasher.update(chunk)
                    except (IOError, PermissionError) as e:
                        print(f"Error reading {file_path}: {e}")
    
    return hasher.hexdigest()


def ptx_db_create(db_path: str):
    """Create the SQLite database and table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS function_db (
            key BLOB PRIMARY KEY,
            value BLOB
        )
    ''')
    conn.commit()
    conn.close()

def ptx_db_insert_entry(db_path: str, key: FunctionDBKey, value: FunctionDBValue):
    """Insert or replace an entry in the database using the key and value objects."""
    key_bytes = key.to_bytes()
    value_bytes = value.to_bytes()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO function_db (key, value) VALUES (?, ?)', (key_bytes, value_bytes))
    conn.commit()
    conn.close()

def ptx_db_get_entry(db_path: str, key: FunctionDBKey) -> FunctionDBValue | None:
    """Retrieve a value from the database using the key object."""
    key_bytes = key.to_bytes()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM function_db WHERE key = ?', (key_bytes,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return FunctionDBValue.from_bytes(result[0])
    return None

def compile_functions(
    arch,
    cuda_code,
    function_names,
    debug = False
):
    annotated_ptx = Program(
        cuda_code,
        code_type="c++", 
        options= \
            ProgramOptions(
                std="c++17",
                arch=f"sm_{arch}",
                device_as_default_execution_space=True,
                # diag_suppress cutlass: 64-D: declaration does not declare anything
                # diag_suppress cutlass: 1055-D: declaration does not declare anything
                diag_suppress=[64,1055],
                ptxas_options=['-v'] if debug else None,
                # Compiling these is a mess.
                define_macro=[
                    "__CUDA_NO_FP8_CONVERSIONS__", 
                    "__CUDA_NO_FP6_CONVERSIONS__",
                    "__CUDA_NO_FP4_CONVERSIONS__"
                ],
                include_path= get_include_paths()
            )
    ).compile(
        "ptx", 
        logs=sys.stdout,
        name_expressions=function_names
    )
    return annotated_ptx

class Singleton(type):
    """Metaclass for creating singleton classes."""
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    
class PtxInjectCache(metaclass=Singleton):
    """Singleton class mapping device IDs to lazily loaded modules/functions."""
    
    def __init__(self, debug = False):
        # A loaded kernel function is stored in device memory also
        # (device_id, function_name) -> Kernel
        self._lock = threading.Lock()
        if debug:
            print(f'(Kermac Debug) Using database at: {cache_root().resolve()}')
        include_dir = get_include_local_cuda_dir()
        kernels_dir = get_local_cuda_kernel_dir()
        self._hash_result = hash_cuda_include_files([include_dir, kernels_dir])
        if debug:
            print(f"(Kermac Debug) Combined hash of cuda source files: {self._hash_result}")
        self._cuda_version = str(torch.version.cuda)
        self._db_path = cache_root().resolve() / 'cache.db'
        os.makedirs(cache_root().resolve(), exist_ok=True)
        ptx_db_create(self._db_path)

    def get_function(
            self,
            device: Device, 
            function_name : str, 
            get_cuda_source_lambda,
            debug = False
        ) -> Any:
        device_id = device.device_id
        if device.compute_capability.major < 8:
            raise ValueError(f"Invalid device compute capability, (device:{device.compute_capability}, requrires at least:8.0")

        function_dict_key = (device_id, function_name)
        with self._lock:
            arch = get_compute_capability(device)
            db_key = FunctionDBKey(
                package_name=get_package_name(),
                package_version=get_package_version(),
                cuda_version=self._cuda_version,
                arch=arch,
                function_name=function_name,
                cuda_source_hash=self._hash_result
            )
            if debug: 
                print(f'(Kermac Debug) Checking database for ptx of function {function_name})')
            db_value = ptx_db_get_entry(self._db_path, db_key)
            if db_value is None:
                cuda_source = get_cuda_source_lambda()
                if debug: 
                    print(f'(Kermac Debug) Mapping does not exist for {db_key}')
                ptx = compile_functions(
                    arch,
                    cuda_source,
                    [function_name],
                    debug
                )
                lowered_name = ptx._sym_map[function_name]
                ptx_data = ptx.code
                db_value = FunctionDBValue(lowered_name, ptx_data)
                ptx_db_insert_entry(self._db_path, db_key, db_value)
                if debug: 
                    print(f'(Kermac Debug) Compiled entry and storing with key: {db_key}')
            else:
                if debug: 
                    print(f'(Kermac Debug) Mapping does exist for {db_key}')
                ptx_data = db_value.ptx_data
                lowered_name = db_value.lowered_name

            return ptx_data.decode('utf-8'), lowered_name
        
