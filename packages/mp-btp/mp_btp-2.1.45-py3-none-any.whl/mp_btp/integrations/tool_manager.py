"""Tool manager - auto detect and install required CLI tools."""
import os
import subprocess
import logging
import stat
import tempfile

logger = logging.getLogger(__name__)

TOOL_DIR = os.environ.get("TOOL_DIR", "/tmp/tool_cache/bin")
TOOL_BASE_URL = "https://github.com/dese8b/b2-migrate/releases/download/b2-tools"

# kubelogin from official release
KUBELOGIN_URL = "https://github.com/int128/kubelogin/releases/download/v1.28.0/kubelogin_linux_amd64.zip"
# cf from official (tar.gz)
CF_URL = "https://packages.cloudfoundry.org/stable?release=linux64-binary&version=v8&source=github"

TOOLS = {
    "btp": f"{TOOL_BASE_URL}/btp",
    "cf": CF_URL,  # Special handling needed
    "kubectl": f"{TOOL_BASE_URL}/kubectl",
    "kubelogin": KUBELOGIN_URL,  # Special handling needed
}


def _ensure_dir():
    os.makedirs(TOOL_DIR, exist_ok=True)
    if TOOL_DIR not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{TOOL_DIR}:{os.environ.get('PATH', '')}"


def _which(tool: str) -> str | None:
    """Check if tool exists in PATH or TOOL_DIR."""
    local_path = os.path.join(TOOL_DIR, tool)
    if os.path.isfile(local_path) and os.access(local_path, os.X_OK):
        return local_path
    for p in os.environ.get("PATH", "").split(":"):
        full = os.path.join(p, tool)
        if os.path.isfile(full) and os.access(full, os.X_OK):
            return full
    return None


def _download(tool: str, url: str) -> bool:
    """Download tool binary."""
    _ensure_dir()
    dest = os.path.join(TOOL_DIR, tool)
    
    try:
        # Handle special tools
        if tool == "kubelogin":
            return _install_kubelogin(url, dest)
        if tool == "cf":
            return _install_cf(url, dest)
        
        logger.info(f"Downloading {tool} from {url}")
        r = subprocess.run(
            ["curl", "-sSL", "-o", dest, "-L", url],
            capture_output=True, timeout=120
        )
        if r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 1000:
            os.chmod(dest, os.stat(dest).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.info(f"{tool} installed to {dest}")
            return True
        logger.error(f"Failed to download {tool}")
        return False
    except Exception as e:
        logger.error(f"Download {tool} failed: {e}")
        return False


def _install_kubelogin(url: str, dest: str) -> bool:
    """Install kubelogin from zip."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "kubelogin.zip")
            logger.info(f"Downloading kubelogin from {url}")
            r = subprocess.run(
                ["curl", "-sSL", "-o", zip_path, "-L", url],
                capture_output=True, timeout=120
            )
            if r.returncode != 0:
                return False
            
            r = subprocess.run(["unzip", "-o", "-q", zip_path, "-d", tmpdir], capture_output=True)
            if r.returncode != 0:
                logger.error(f"Unzip failed: {r.stderr.decode()}")
                return False
            
            # Find kubelogin binary in extracted files
            src = os.path.join(tmpdir, "kubelogin")
            if os.path.isfile(src):
                subprocess.run(["cp", src, dest], check=True)
                os.chmod(dest, 0o755)
                # Create kubectl-oidc_login symlink (required by kubeconfig)
                oidc_link = os.path.join(os.path.dirname(dest), "kubectl-oidc_login")
                if not os.path.exists(oidc_link):
                    os.symlink(dest, oidc_link)
                logger.info(f"kubelogin installed to {dest}")
                return True
            
            logger.error("kubelogin binary not found in zip")
            return False
    except Exception as e:
        logger.error(f"Install kubelogin failed: {e}")
        return False


def _install_cf(url: str, dest: str) -> bool:
    """Install cf CLI from tar.gz."""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tgz_path = os.path.join(tmpdir, "cf.tgz")
            logger.info(f"Downloading cf from {url}")
            r = subprocess.run(
                ["curl", "-sSL", "-o", tgz_path, "-L", url],
                capture_output=True, timeout=120
            )
            if r.returncode != 0:
                return False
            
            r = subprocess.run(["tar", "-xzf", tgz_path, "-C", tmpdir], capture_output=True)
            if r.returncode != 0:
                logger.error(f"Untar failed: {r.stderr.decode()}")
                return False
            
            # cf binary should be directly in tmpdir
            src = os.path.join(tmpdir, "cf8")
            if not os.path.isfile(src):
                src = os.path.join(tmpdir, "cf")
            
            if os.path.isfile(src):
                subprocess.run(["cp", src, dest], check=True)
                os.chmod(dest, 0o755)
                logger.info(f"cf installed to {dest}")
                return True
            
            logger.error("cf binary not found in tar")
            return False
    except Exception as e:
        logger.error(f"Install cf failed: {e}")
        return False


def ensure_tool(tool: str) -> bool:
    """Ensure a tool is available, download if missing."""
    if _which(tool):
        return True
    if tool not in TOOLS:
        logger.warning(f"Unknown tool: {tool}")
        return False
    return _download(tool, TOOLS[tool])


def ensure_tools(tools: list[str] = None) -> dict[str, bool]:
    """Ensure multiple tools are available."""
    if tools is None:
        tools = list(TOOLS.keys())
    return {t: ensure_tool(t) for t in tools}


def get_tool_path(tool: str) -> str | None:
    """Get full path to tool, installing if needed."""
    ensure_tool(tool)
    return _which(tool)


def check_tools() -> dict[str, str | None]:
    """Check status of all tools without installing."""
    return {t: _which(t) for t in TOOLS}
