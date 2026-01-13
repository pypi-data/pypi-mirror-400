# Copyright The Aliyun Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import subprocess
import sys

from ctyun.bootstrap.bootstrap_gen import (
    libraries,
)
import requests
import os
import shutil
import time

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

import tarfile
import glob
from ctyun.bootstrap.version import __version__
from ctyun.bootstrap.utils import get_agent_path, check_network

logger = logging.getLogger(__name__)


def format_error(message):
    """Format an error message with special characters to make it stand out"""
    return f"!!! ERROR: {message} !!!"

def format_warning(message):
    """Format a warning message with special characters to make it stand out"""
    return f"*** WARNING: {message} ***"

def _syscall(func):
    def wrapper(package=None):
        try:
            if package:
                return func(package)
            return func()
        except subprocess.SubprocessError as exp:
            cmd = getattr(exp, "cmd", None)
            msg = str(exp)  # Default error message
            if cmd:
                msg = f'Error calling system command "{" ".join(cmd)}"'
            if package:
                msg = f'{msg} for package "{package}"'
            raise RuntimeError(msg)

    return wrapper


def _bulk_pip_install(packages, pip_path):
    """
    Install multiple packages at once to a custom target path with progress bar.
    
    Args:
        packages: List of package paths to install
        pip_path: Custom installation path
    """
    print(f"Installing {len(packages)} packages to {pip_path}...")
    
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target", 
        pip_path,  # 安装到包专用目录
        "--no-cache-dir",
    ]
    cmd.extend(packages)  # Add all packages to the command
    
    if TQDM_AVAILABLE:
        # Show progress for each package
        with tqdm(total=len(packages), desc="Installing packages", unit="pkg") as pbar:
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            last_package = ""
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                # Check if a new package installation has started
                if "Processing " in line and "/" in line:
                    current_package = line.split("/")[-1].strip()
                    if current_package != last_package:
                        last_package = current_package
                        pbar.update(1)
                        pbar.set_description(f"Installing {current_package[:30]}")
            
            if process.returncode != 0:
                error = process.stderr.read()
                raise subprocess.SubprocessError(f"Installation failed: {error}")
    else:
        # Fallback if tqdm is not available
        subprocess.check_call(cmd)
    
    print(f"Successfully installed {len(packages)} packages!")


@_syscall
def _sys_pip_install(package):
    if os.getenv("PIPPATH") is not None:
        pip_path = os.getenv("PIPPATH")
        # Check if package is a list of packages (for bulk installation)
        if isinstance(package, list):
            _bulk_pip_install(package, pip_path)
        else:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--target", 
                    pip_path,  # 安装到包专用目录
                    package,
                    "--no-cache-dir",
                ]
            )
    else:
        # explicit upgrade strategy to override potential pip config
        cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-U",
                # 强制重装，防止前后不兼容
                "--force-reinstall",
                "--upgrade-strategy",
                "only-if-needed",
            ]
        
        # Check if package is a list of packages for bulk installation
        if isinstance(package, list):
            print(f"Installing {len(package)} packages...")
            cmd.extend(package)  # Add all packages to the command
            
            if TQDM_AVAILABLE:
                # Show progress for each package
                with tqdm(total=len(package), desc="Installing packages", unit="pkg") as pbar:
                    process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    
                    last_package = ""
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        
                        # Check if a new package installation has started
                        if "Processing " in line and "/" in line:
                            current_package = line.split("/")[-1].strip()
                            if current_package != last_package:
                                last_package = current_package
                                pbar.update(1)
                                pbar.set_description(f"Installing {current_package[:30]}")
                    
                    if process.returncode != 0:
                        error = process.stderr.read()
                        raise subprocess.SubprocessError(f"Installation failed: {error}")
                
                print(f"Successfully installed {len(package)} packages!")
            else:
                # Fallback if tqdm is not available
                subprocess.check_call(cmd)
        else:
            cmd.append(package)
            subprocess.check_call(cmd)


file_path = 'ctyun-python-agent.tar.gz'
whl_path = "./ctyun-python-agent"


# 通过region，version等信息 安装对应的安装包
def get_download_path() -> str:
    # This function appears to be unfinished/unused
    # Placeholder for future functionality
    return None


def _download_with_progress(url, file_path):
    """
    Download a file with progress bar
    """
    print(f"Downloading agent from {url}...")
    headers = {
    'x-regionid': 'b342b77ef26b11ecb0ac0242ac110002'
    }
    try:
        # Add timeout to prevent hanging indefinitely
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        
        total_size = int(response.headers.get('content-length', 0))
        
        if TQDM_AVAILABLE and total_size > 0:
            with open(file_path, 'wb') as f, tqdm(
                desc="Downloading",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)
        else:
            # Fallback if tqdm is not available
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print("Download complete!")
        
        return True
    except requests.exceptions.Timeout:
        print(format_error("Download timed out. Please check your network connection and try again."))
        return False
    except requests.exceptions.ConnectionError:
        print(format_error("Network connection error. Please check your internet connection."))
        return False
    except requests.exceptions.HTTPError as e:
        print(format_error(f"HTTP error occurred: {e}"))
        return False
    except Exception as e:
        print(format_error(f"Failed to download agent: {e}"))
        return False


def _download_agent_file(env):
    url = get_agent_path(env)
    if url is None:
        print(f"agent download url: {url}")
    else:
        print(f"agent download url: {url}")
    
    if url is None:
        logger.error(f"get agent url err! ")
        print(format_error("Failed to get agent URL!"))
        return False
    
    # Check network connectivity before attempting download
    print("Checking network connectivity...")
    if not check_network(url, timeout=5):
        print(format_error(f"Network connection to {url} failed."))
        print(format_error("Please check your internet connection and try again."))
        return False
    
    # Download with progress bar
    return _download_with_progress(url, file_path)


def _remove_agent_file():
    os.remove(file_path)
    shutil.rmtree(whl_path)


def _extract_whl():
    os.makedirs(whl_path, exist_ok=True)
    
    print("Extracting wheels from archive...")
    # 打开并解压缩 tar.gz 文件
    if TQDM_AVAILABLE:
        with tarfile.open(file_path, 'r:gz') as tar:
            members = tar.getmembers()
            with tqdm(total=len(members), desc="Extracting files", unit="file") as pbar:
                for member in members:
                    tar.extract(member, path=whl_path)
                    pbar.update(1)
    else:
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=whl_path)
    
    # 找到所有的 .whl 文件
    whl_files = glob.glob(f'{whl_path}/*/*.whl')
    print(f"Found {len(whl_files)} wheel files")
    return whl_files


def _pip_check():
    """Ensures none of the instrumentations have dependency conflicts.
    Clean check reported as:
    'No broken requirements found.'
    Dependency conflicts are reported as:
    'opentelemetry-instrumentation-flask 1.0.1 has requirement opentelemetry-sdk<2.0,>=1.0, but you have opentelemetry-sdk 0.5.'
    To not be too restrictive, we'll only check for relevant packages.
    """
    with subprocess.Popen(
            [sys.executable, "-m", "pip", "check"], stdout=subprocess.PIPE
    ) as check_pipe:
        pip_check = check_pipe.communicate()[0].decode()
        pip_check_lower = pip_check.lower()
    for package_tup in libraries:
        for package in package_tup:
            if package.lower() in pip_check_lower:
                raise RuntimeError(f"Dependency conflict found: {pip_check}")


def _run_install(env):
    print("\nStarting Ctyun Python Agent installation...")

    download_success = _download_agent_file(env)
    if not download_success:
        print(format_error("Installation aborted due to download failure."))
        return
    
    agent_whls = ["opentelemetry-distro", "opentelemetry-exporter-otlp"]
    agent_whls.extend(_extract_whl())
    print("plugins .... ", agent_whls)
    
    if os.getenv("PIPPATH") is not None:
        pip_path = os.getenv("PIPPATH")
        # Install all wheel files at once to ensure dependencies are resolved correctly
        _sys_pip_install(agent_whls)
        # Create sitecustomize.py to automatically load the agent
        # _create_sitecustomize(pip_path)
    else:
        # Install all wheel files at once for the default installation path as well
        _sys_pip_install(agent_whls)

    print("installing opentelemetry instrument...")
    
    cmd = 'opentelemetry-bootstrap -a install'  # 列出所有 .py 文件（Linux/macOS）
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    print(result.stdout)

    _pip_check()
    _remove_agent_file()



def run() -> None:
    action_install = "install"
    action_requirements = "requirements"
    action_uninstall = "uninstall"

    parser = argparse.ArgumentParser(
        description="""
        ctyun-bootstrap detects installed libraries and automatically
        installs the relevant instrumentation packages for them.
        """
    )

    parser.add_argument(
        "-a",
        "--action",
        choices=[action_install, action_requirements, action_uninstall],
        default=action_requirements,
        help="""
        install - uses pip to install the new requirements using to the
                  currently active site-package.
        requirements - prints out the new requirements to stdout. Action can
                       be piped and appended to a requirements.txt file.
        """,
    )
    
    # Add install-specific arguments

    parser.add_argument(
        "-v",
        "--version",
        help="Specify the agent version to install",
    )

    parser.add_argument(
        "-env",
        "--environment",
        default="prod",
        help="Specify the agent version to install",
    )
    
    args = parser.parse_args()
    
    # Set environment variables based on arguments
    if args.version:
        os.environ["VERSION"] = args.version
        print(f"Using agent version: {args.version}")

    cmd = {
        action_install: lambda: _run_install(args.environment),
    }[args.action]
    cmd()
