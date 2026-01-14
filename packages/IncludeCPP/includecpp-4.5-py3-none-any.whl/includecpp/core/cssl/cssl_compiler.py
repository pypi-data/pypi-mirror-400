"""
CSSL Compiler Configuration - Manages C++ acceleration setup.

This module handles:
- Automatic compiler detection (g++, clang++, cl)
- Platform detection for pre-built module matching
- Configuration storage in %APPDATA%/IncludeCPP/cssl/
- Local compilation when no pre-built module exists

The config is stored once on first run and reused for subsequent runs.
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List


def get_cssl_config_dir() -> Path:
    """
    Get CSSL config directory in APPDATA.

    Returns:
        Windows: %APPDATA%/IncludeCPP/cssl/
        Linux/macOS: ~/.config/IncludeCPP/cssl/
    """
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path.home() / '.config'

    config_dir = base / 'IncludeCPP' / 'cssl'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cssl_config_path() -> Path:
    """Get path to CSSL config file."""
    return get_cssl_config_dir() / 'cssl_config.json'


def get_cssl_build_dir() -> Path:
    """
    Get directory for locally-built CSSL modules.

    Returns:
        Windows: %APPDATA%/IncludeCPP/cssl/build/
        Linux/macOS: ~/.config/IncludeCPP/cssl/build/
    """
    build_dir = get_cssl_config_dir() / 'build'
    build_dir.mkdir(parents=True, exist_ok=True)
    return build_dir


class CSSLCompilerConfig:
    """
    Manages CSSL C++ acceleration configuration.

    Handles compiler detection, platform info, and configuration persistence.
    Config is stored in %APPDATA%/IncludeCPP/cssl/cssl_config.json
    """

    def __init__(self):
        self.config_path = get_cssl_config_path()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from file, or return empty dict if not exists."""
        if self.config_path.exists():
            try:
                return json.loads(self.config_path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_config(self):
        """Save config to file."""
        try:
            self.config_path.write_text(
                json.dumps(self.config, indent=2),
                encoding='utf-8'
            )
        except OSError:
            pass

    def detect_compiler(self) -> Optional[str]:
        """
        Detect available C++ compiler.

        Checks in order: g++, clang++, cl (MSVC)

        Returns:
            Compiler command name, or None if no compiler found
        """
        compilers = ['g++', 'clang++']

        # On Windows, also check for cl (MSVC)
        if sys.platform == 'win32':
            compilers.append('cl')

        for compiler in compilers:
            if shutil.which(compiler):
                # Verify compiler works
                try:
                    result = subprocess.run(
                        [compiler, '--version'],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return compiler
                except (subprocess.SubprocessError, OSError):
                    continue

        return None

    def detect_compiler_version(self, compiler: str) -> Optional[str]:
        """Get compiler version string."""
        try:
            result = subprocess.run(
                [compiler, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Return first line of version output
                return result.stdout.split('\n')[0].strip()
        except (subprocess.SubprocessError, OSError):
            pass
        return None

    def detect_platform(self) -> Dict[str, str]:
        """
        Detect platform info for pre-built module matching.

        Returns:
            Dict with: system, machine, python_version, platform
        """
        return {
            'system': platform.system(),           # Windows, Linux, Darwin
            'machine': platform.machine(),          # x86_64, AMD64, arm64
            'python_version': f"{sys.version_info.major}{sys.version_info.minor}",
            'python_full_version': platform.python_version(),
            'platform': sys.platform,               # win32, linux, darwin
        }

    def get_prebuilt_suffix(self) -> str:
        """
        Get expected suffix for pre-built module based on platform.

        Returns:
            Platform-specific module suffix like .cp312-win_amd64.pyd
        """
        info = self.detect_platform()
        py_ver = info['python_version']

        if info['platform'] == 'win32':
            return f".cp{py_ver}-win_amd64.pyd"
        elif info['platform'] == 'linux':
            return f".cpython-{py_ver}-x86_64-linux-gnu.so"
        elif info['platform'] == 'darwin':
            arch = 'arm64' if info['machine'] == 'arm64' else 'x86_64'
            return f".cpython-{py_ver}-{arch}-darwin.so"

        # Fallback
        return ".pyd" if info['platform'] == 'win32' else ".so"

    def get_all_possible_suffixes(self) -> List[str]:
        """
        Get all possible module suffixes for current platform.

        Returns:
            List of suffixes to try, in order of preference
        """
        info = self.detect_platform()
        py_ver = info['python_version']

        suffixes = [self.get_prebuilt_suffix()]

        if info['platform'] == 'win32':
            suffixes.extend(['.pyd', f'.cp{py_ver}-win32.pyd'])
        elif info['platform'] == 'linux':
            suffixes.extend(['.so', f'.cpython-{py_ver}-linux-gnu.so'])
        elif info['platform'] == 'darwin':
            suffixes.extend(['.so', '.dylib'])

        return suffixes

    def setup_first_run(self) -> Dict[str, Any]:
        """
        First-run setup - detect and store compiler/platform info.

        Called automatically on first CSSL import. Detects compiler
        and platform, stores in config file for future runs.

        Returns:
            The config dict
        """
        # Only run setup once
        if self.config.get('initialized'):
            return self.config

        compiler = self.detect_compiler()
        compiler_version = None
        if compiler:
            compiler_version = self.detect_compiler_version(compiler)

        platform_info = self.detect_platform()

        self.config = {
            'initialized': True,
            'compiler': compiler,
            'compiler_version': compiler_version,
            'platform': platform_info,
            'cpp_available': compiler is not None,
            'prebuilt_suffix': self.get_prebuilt_suffix(),
            'build_dir': str(get_cssl_build_dir()),
        }

        self._save_config()
        return self.config

    def refresh(self) -> Dict[str, Any]:
        """
        Force refresh of compiler/platform detection.

        Use this if user installed a new compiler.

        Returns:
            Updated config dict
        """
        self.config['initialized'] = False
        return self.setup_first_run()

    def can_compile(self) -> bool:
        """Check if local compilation is possible."""
        if not self.config.get('initialized'):
            self.setup_first_run()
        return self.config.get('compiler') is not None

    def get_compiler(self) -> Optional[str]:
        """Get configured compiler."""
        if not self.config.get('initialized'):
            self.setup_first_run()
        return self.config.get('compiler')

    def get_platform_info(self) -> Dict[str, str]:
        """Get stored platform info."""
        if not self.config.get('initialized'):
            self.setup_first_run()
        return self.config.get('platform', self.detect_platform())

    def get_build_dir(self) -> Path:
        """Get local build directory for compiled modules."""
        return get_cssl_build_dir()


def compile_cssl_core(force: bool = False) -> Optional[Path]:
    """
    Compile cssl_core module locally.

    Uses the detected compiler to build cssl_core from source.
    The compiled module is stored in %APPDATA%/IncludeCPP/cssl/build/

    Args:
        force: If True, rebuild even if module already exists

    Returns:
        Path to compiled module, or None if compilation failed
    """
    config = CSSLCompilerConfig()
    config.setup_first_run()

    if not config.can_compile():
        return None

    build_dir = config.get_build_dir()
    suffix = config.get_prebuilt_suffix()
    output_path = build_dir / f'cssl_core{suffix}'

    # Check if already built
    if output_path.exists() and not force:
        return output_path

    # Get source directory
    cssl_dir = Path(__file__).parent
    cpp_dir = cssl_dir / 'cpp'
    source_dir = cpp_dir / 'include'

    source_file = source_dir / 'cssl_core.cpp'
    if not source_file.exists():
        return None

    # Try to build using includecpp
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'includecpp', 'rebuild', '--clean'],
            cwd=cpp_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            # Find the built module and copy to our build dir
            # IncludeCPP outputs to APPDATA, we need to find and copy
            appdata = Path(os.environ.get('APPDATA', ''))
            icpp_build = appdata / 'cssl_core-g-build-proj' / 'bindings'

            for suffix_try in config.get_all_possible_suffixes():
                src = icpp_build / f'api{suffix_try}'
                if src.exists():
                    shutil.copy2(src, output_path)
                    return output_path

    except (subprocess.SubprocessError, OSError, ImportError):
        pass

    return None


def get_cssl_core_path() -> Optional[Path]:
    """
    Get path to cssl_core module, checking all locations.

    Checks in order:
    1. Bundled module in package (cpp/build/)
    2. Locally compiled module in APPDATA

    Returns:
        Path to module, or None if not found
    """
    config = CSSLCompilerConfig()
    config.setup_first_run()

    suffixes = config.get_all_possible_suffixes()

    # 1. Check bundled locations
    cssl_dir = Path(__file__).parent
    bundled_dirs = [
        cssl_dir / 'cpp' / 'build',
        cssl_dir / 'bin',
    ]

    for dir_path in bundled_dirs:
        if not dir_path.exists():
            continue
        for suffix in suffixes:
            module_path = dir_path / f'cssl_core{suffix}'
            if module_path.exists():
                return module_path

    # 2. Check APPDATA build location
    build_dir = config.get_build_dir()
    for suffix in suffixes:
        module_path = build_dir / f'cssl_core{suffix}'
        if module_path.exists():
            return module_path

    return None
