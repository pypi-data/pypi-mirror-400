"""PostgreSQL binary download and management.

Downloads pre-built PostgreSQL binaries for the current platform.
Uses PostgreSQL embedded builds from zonkyio/embedded-postgres-binaries.

Supports:
- Windows x64
- macOS x64 and arm64 (Apple Silicon)
- Linux x64 and arm64
"""

import hashlib
import platform
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
import ssl
import certifi

import structlog

logger = structlog.get_logger()

# PostgreSQL version to download
PG_VERSION = "16.2.0"

# pgvector version
PGVECTOR_VERSION = "0.8.0"

# Binary distribution URLs (zonkyio/embedded-postgres-binaries releases)
# These are self-contained PostgreSQL distributions optimized for embedding
BINARY_BASE_URL = "https://repo1.maven.org/maven2/io/zonky/test/postgres/embedded-postgres-binaries"

# pgvector binary URLs per platform
# Windows: Pre-compiled from andreiramani/pgvector_pgsql_windows
# macOS/Linux: Built from source or use package managers
PGVECTOR_URLS = {
    "windows-amd64": f"https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/0.8.0_16.6/vector.v{PGVECTOR_VERSION}-pg16.zip",
    # macOS and Linux users should use: brew install pgvector or apt install postgresql-16-pgvector
}


@dataclass
class PlatformInfo:
    """Platform detection result."""

    os: str  # windows, darwin, linux
    arch: str  # amd64, arm64
    archive_ext: str  # .zip for windows, .txz for others
    binary_suffix: str  # .exe for windows, empty for others

    @property
    def artifact_name(self) -> str:
        """Maven artifact name for this platform."""
        os_map = {
            "windows": "windows",
            "darwin": "darwin",
            "linux": "linux",
        }
        arch_map = {
            "amd64": "amd64",
            "arm64": "arm64v8",
            "x86_64": "amd64",
        }
        return f"{os_map[self.os]}-{arch_map[self.arch]}"

    @property
    def download_url(self) -> str:
        """Full download URL for PostgreSQL binaries."""
        artifact = self.artifact_name
        ext = "jar" if self.os == "windows" else "jar"
        return (
            f"{BINARY_BASE_URL}-{artifact}/{PG_VERSION}/"
            f"embedded-postgres-binaries-{artifact}-{PG_VERSION}.{ext}"
        )


def detect_platform() -> PlatformInfo:
    """Detect current platform for binary selection."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize OS
    if system == "windows":
        os_name = "windows"
        archive_ext = ".zip"
        binary_suffix = ".exe"
    elif system == "darwin":
        os_name = "darwin"
        archive_ext = ".txz"
        binary_suffix = ""
    elif system == "linux":
        os_name = "linux"
        archive_ext = ".txz"
        binary_suffix = ""
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    # Normalize architecture
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    return PlatformInfo(
        os=os_name,
        arch=arch,
        archive_ext=archive_ext,
        binary_suffix=binary_suffix,
    )


class PostgresBinaryManager:
    """Manages PostgreSQL binary downloads and extraction.

    Binaries are downloaded once and cached in the user's data directory.
    Location: ~/.mind/postgres/{version}/{platform}/
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize binary manager.

        Args:
            base_dir: Base directory for storing binaries.
                     Defaults to ~/.mind/postgres/
        """
        if base_dir is None:
            base_dir = Path.home() / ".mind" / "postgres"

        self.base_dir = base_dir
        self.platform = detect_platform()
        self.version = PG_VERSION

        # Directory structure:
        # ~/.mind/postgres/
        #   └── 16.2.0/
        #       └── darwin-arm64/
        #           ├── bin/
        #           ├── lib/
        #           ├── share/
        #           └── ...
        self.install_dir = (
            self.base_dir / self.version / self.platform.artifact_name
        )

        self._log = logger.bind(
            platform=self.platform.artifact_name,
            version=self.version,
            install_dir=str(self.install_dir),
        )

    @property
    def bin_dir(self) -> Path:
        """Directory containing PostgreSQL executables."""
        # Windows binaries are flat in install_dir, not in bin/
        if self.platform.os == "windows":
            return self.install_dir
        return self.install_dir / "bin"

    @property
    def lib_dir(self) -> Path:
        """Directory containing PostgreSQL libraries."""
        # Windows has DLLs flat in install_dir, not in lib/
        if self.platform.os == "windows":
            return self.install_dir
        return self.install_dir / "lib"

    @property
    def share_dir(self) -> Path:
        """Directory containing PostgreSQL share files."""
        # Windows has share files flat in install_dir, not in share/
        if self.platform.os == "windows":
            return self.install_dir
        return self.install_dir / "share"

    def postgres_binary(self) -> Path:
        """Path to postgres executable."""
        suffix = self.platform.binary_suffix
        return self.bin_dir / f"postgres{suffix}"

    def pg_ctl_binary(self) -> Path:
        """Path to pg_ctl executable."""
        suffix = self.platform.binary_suffix
        return self.bin_dir / f"pg_ctl{suffix}"

    def initdb_binary(self) -> Path:
        """Path to initdb executable."""
        suffix = self.platform.binary_suffix
        return self.bin_dir / f"initdb{suffix}"

    def psql_binary(self) -> Path:
        """Path to psql executable."""
        suffix = self.platform.binary_suffix
        return self.bin_dir / f"psql{suffix}"

    def is_installed(self) -> bool:
        """Check if PostgreSQL binaries are installed."""
        return (
            self.postgres_binary().exists() and
            self.pg_ctl_binary().exists() and
            self.initdb_binary().exists()
        )

    def ensure_installed(self) -> Path:
        """Ensure PostgreSQL binaries are installed, downloading if needed.

        Returns:
            Path to the installation directory

        Raises:
            RuntimeError: If download or extraction fails
        """
        if self.is_installed():
            self._log.debug("postgres_binaries_found")
            # Still need to set up Windows paths each time
            if self.platform.os == "windows":
                self._setup_windows_paths()
            return self.install_dir

        self._log.info("postgres_binaries_not_found", action="downloading")
        self._download_and_extract()

        # Set up Windows-specific paths for hardcoded PostgreSQL paths
        if self.platform.os == "windows":
            self._setup_windows_paths()

        if not self.is_installed():
            raise RuntimeError(
                f"PostgreSQL installation incomplete. "
                f"Expected binaries in {self.bin_dir}"
            )

        self._log.info("postgres_binaries_installed")
        return self.install_dir

    def _download_and_extract(self) -> None:
        """Download and extract PostgreSQL binaries."""
        url = self.platform.download_url
        self._log.info("downloading_postgres", url=url)

        # Create temp directory for download
        temp_dir = self.base_dir / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        jar_path = temp_dir / f"postgres-{self.version}.jar"

        try:
            # Download the JAR file
            self._download_file(url, jar_path)

            # Extract the JAR (it's just a ZIP)
            self._log.debug("extracting_postgres_jar")
            self.install_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(jar_path, 'r') as jar:
                # Find the inner archive (postgres-*.txz or postgres-*.zip)
                inner_archives = [
                    n for n in jar.namelist()
                    if n.startswith("postgres-") and (
                        n.endswith(".txz") or n.endswith(".zip")
                    )
                ]

                if not inner_archives:
                    raise RuntimeError(
                        f"No PostgreSQL archive found in JAR. "
                        f"Contents: {jar.namelist()[:10]}"
                    )

                inner_archive = inner_archives[0]
                self._log.debug("extracting_inner_archive", name=inner_archive)

                # Extract inner archive to temp
                inner_path = temp_dir / inner_archive
                with jar.open(inner_archive) as src, open(inner_path, 'wb') as dst:
                    shutil.copyfileobj(src, dst)

            # Extract the inner archive
            if inner_path.suffix == ".txz":
                self._extract_txz(inner_path, self.install_dir)
            else:
                self._extract_zip(inner_path, self.install_dir)

            # Make binaries executable on Unix
            if self.platform.os != "windows":
                self._make_executable()

        finally:
            # Cleanup temp files
            if jar_path.exists():
                jar_path.unlink()
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _download_file(self, url: str, dest: Path) -> None:
        """Download a file with progress logging."""
        self._log.debug("download_starting", url=url, dest=str(dest))

        # Create SSL context with certifi certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        request = Request(
            url,
            headers={"User-Agent": "mind-sdk/1.0"},
        )

        try:
            with urlopen(request, timeout=300, context=ssl_context) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0

                with open(dest, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            pct = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                self._log.debug(
                                    "download_progress",
                                    downloaded_mb=downloaded // (1024 * 1024),
                                    total_mb=total_size // (1024 * 1024),
                                    percent=f"{pct:.1f}%",
                                )

                self._log.info(
                    "download_complete",
                    size_mb=downloaded // (1024 * 1024),
                )

        except URLError as e:
            raise RuntimeError(f"Failed to download PostgreSQL: {e}") from e

    def _extract_txz(self, archive: Path, dest: Path) -> None:
        """Extract a .txz (tar.xz) archive."""
        import lzma

        self._log.debug("extracting_txz", archive=str(archive))

        with lzma.open(archive) as xz:
            with tarfile.open(fileobj=xz) as tar:
                # Extract all files, stripping the first directory component
                for member in tar.getmembers():
                    # Strip leading directory (e.g., "pgsql/" or "postgres/")
                    parts = Path(member.name).parts
                    if len(parts) > 1:
                        member.name = str(Path(*parts[1:]))
                        tar.extract(member, dest)

    def _extract_zip(self, archive: Path, dest: Path) -> None:
        """Extract a .zip archive."""
        self._log.debug("extracting_zip", archive=str(archive))

        with zipfile.ZipFile(archive, 'r') as zf:
            for member in zf.namelist():
                # Strip leading directory
                parts = Path(member).parts
                if len(parts) > 1:
                    target = dest / Path(*parts[1:])
                    if member.endswith('/'):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target, 'wb') as dst:
                            shutil.copyfileobj(src, dst)

    def _make_executable(self) -> None:
        """Make all binaries executable on Unix."""
        import stat

        if not self.bin_dir.exists():
            return

        for binary in self.bin_dir.iterdir():
            if binary.is_file():
                mode = binary.stat().st_mode
                binary.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def cleanup(self) -> None:
        """Remove installed binaries."""
        if self.install_dir.exists():
            self._log.info("cleaning_postgres_binaries", dir=str(self.install_dir))
            shutil.rmtree(self.install_dir)

    def is_pgvector_installed(self) -> bool:
        """Check if pgvector extension is installed."""
        if self.platform.os == "windows":
            # Check for vector.dll in lib directory
            vector_dll = self.lib_dir / "vector.dll"
            return vector_dll.exists()
        else:
            # Check for vector.so in lib directory
            vector_so = self.lib_dir / "vector.so"
            return vector_so.exists()

    def ensure_pgvector_installed(self) -> bool:
        """Ensure pgvector extension is installed.

        Returns:
            True if pgvector is available, False if not supported on this platform
        """
        if self.is_pgvector_installed():
            self._log.debug("pgvector_already_installed")
            return True

        platform_key = self.platform.artifact_name
        if platform_key not in PGVECTOR_URLS:
            self._log.warning(
                "pgvector_not_available_for_platform",
                platform=platform_key,
                message="pgvector binaries not available. Install manually: "
                        "brew install pgvector (macOS) or apt install postgresql-16-pgvector (Linux)"
            )
            return False

        self._log.info("installing_pgvector", version=PGVECTOR_VERSION)
        self._download_and_install_pgvector()
        return True

    def _download_and_install_pgvector(self) -> None:
        """Download and install pgvector extension."""
        platform_key = self.platform.artifact_name
        url = PGVECTOR_URLS[platform_key]

        self._log.info("downloading_pgvector", url=url)

        # Create temp directory
        temp_dir = self.base_dir / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        zip_path = temp_dir / "pgvector.zip"

        try:
            # Download pgvector
            self._download_file(url, zip_path)

            # Extract pgvector
            self._log.debug("extracting_pgvector")
            extract_dir = temp_dir / "pgvector"
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)

            # Install pgvector files to PostgreSQL directories
            self._install_pgvector_files(extract_dir)

            self._log.info("pgvector_installed", version=PGVECTOR_VERSION)

        finally:
            # Cleanup
            if zip_path.exists():
                zip_path.unlink()
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _install_pgvector_files(self, extract_dir: Path) -> None:
        """Install pgvector files to PostgreSQL directories."""
        if self.platform.os == "windows":
            # Windows structure: lib/vector.dll, share/extension/*.sql

            # Find and copy vector.dll
            for dll in extract_dir.rglob("vector.dll"):
                dst = self.lib_dir / "vector.dll"
                self._log.debug("copying_pgvector_dll", src=str(dll), dst=str(dst))
                shutil.copy2(dll, dst)

                # Also copy to C:\lib for hardcoded paths
                try:
                    lib_dir = Path("C:/lib")
                    lib_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dll, lib_dir / "vector.dll")
                except PermissionError:
                    self._log.warning("could_not_copy_to_c_lib", message="Run as admin for full support")
                break

            # Find and copy extension files
            for sql_file in extract_dir.rglob("*.sql"):
                dst = self.share_dir / "extension" / sql_file.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sql_file, dst)

                # Also copy to C:\share\extension
                try:
                    share_ext = Path("C:/share/extension")
                    share_ext.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sql_file, share_ext / sql_file.name)
                except PermissionError:
                    pass

            # Copy .control file
            for ctrl_file in extract_dir.rglob("*.control"):
                dst = self.share_dir / "extension" / ctrl_file.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ctrl_file, dst)

                try:
                    share_ext = Path("C:/share/extension")
                    shutil.copy2(ctrl_file, share_ext / ctrl_file.name)
                except PermissionError:
                    pass

        else:
            # Unix: lib/vector.so, share/extension/*.sql
            for so_file in extract_dir.rglob("vector.so"):
                dst = self.lib_dir / "vector.so"
                shutil.copy2(so_file, dst)
                break

            for sql_file in extract_dir.rglob("*.sql"):
                dst = self.share_dir / "extension" / sql_file.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sql_file, dst)

            for ctrl_file in extract_dir.rglob("*.control"):
                dst = self.share_dir / "extension" / ctrl_file.name
                shutil.copy2(ctrl_file, dst)

    def _setup_windows_paths(self) -> None:
        """Set up Windows-specific paths for hardcoded PostgreSQL paths.

        The zonkyio embedded-postgres binaries have hardcoded Unix paths like
        /share/timezone and /lib that don't exist on Windows. This method
        creates those paths and copies the required files there.

        This is a workaround for the embedded binaries' hardcoded paths.
        The paths created are:
        - C:\\share (timezone, timezonesets, tsearch_data, extension, etc.)
        - C:\\lib (DLLs for extensions)
        """
        self._log.debug("setting_up_windows_paths")

        share_dir = Path("C:/share")
        lib_dir = Path("C:/lib")

        # Create share directory structure
        try:
            share_dir.mkdir(parents=True, exist_ok=True)

            # Copy share subdirectories
            subdirs_to_copy = [
                "timezone", "timezonesets", "tsearch_data",
                "extension", "contrib", "locale"
            ]
            for subdir in subdirs_to_copy:
                src = self.install_dir / subdir
                dst = share_dir / subdir
                if src.exists() and not dst.exists():
                    shutil.copytree(src, dst)

            # Copy share files
            for pattern in ["*.sql", "*.bki", "*.txt", "*.sample"]:
                for src_file in self.install_dir.glob(pattern):
                    dst_file = share_dir / src_file.name
                    if not dst_file.exists():
                        shutil.copy2(src_file, dst_file)

        except PermissionError:
            self._log.warning(
                "windows_share_path_permission_denied",
                path=str(share_dir),
                message="Could not create C:\\share - may need admin rights. "
                        "Run as administrator or manually create this directory."
            )

        # Create lib directory with DLLs
        try:
            lib_dir.mkdir(parents=True, exist_ok=True)

            # Copy DLLs to lib directory
            for dll in self.install_dir.glob("*.dll"):
                dst = lib_dir / dll.name
                if not dst.exists():
                    shutil.copy2(dll, dst)

        except PermissionError:
            self._log.warning(
                "windows_lib_path_permission_denied",
                path=str(lib_dir),
                message="Could not create C:\\lib - may need admin rights. "
                        "Run as administrator or manually create this directory."
            )

        self._log.debug("windows_paths_setup_complete")
