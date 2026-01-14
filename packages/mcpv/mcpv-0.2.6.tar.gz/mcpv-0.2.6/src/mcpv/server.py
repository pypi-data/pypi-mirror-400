import os
import subprocess
import logging
import sys
from pathlib import Path
from fastmcp import FastMCP
from .valve import valve
from .vault import manager

# 1. 로깅 및 설정 폴더
CONFIG_DIR = Path.home() / ".gemini" / "antigravity"
LOG_DIR = CONFIG_DIR
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except:
    pass

LOG_FILE = LOG_DIR / "mcpv_debug.log"
ROOT_PATH_FILE = CONFIG_DIR / "root_path.txt"

# 기존 핸들러 제거
root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger("mcpv-server")

# 2. 실행 위치 감지 (파일 기반)
# Antigravity가 환경변수를 날려버려도, 파일은 남아있습니다.
if ROOT_PATH_FILE.exists():
    try:
        content = ROOT_PATH_FILE.read_text(encoding="utf-8").strip()
        ROOT_DIR = Path(content).resolve()
        source = "FILE(root_path.txt)"
    except Exception as e:
        ROOT_DIR = Path.cwd().resolve()
        source = f"CWD(File Read Error: {e})"
else:
    ROOT_DIR = Path.cwd().resolve()
    source = "CWD(File Not Found)"

logger.info("="*40)
logger.info(f"🚀 MCPV Server Started.")
logger.info(f"📂 Project Root: {ROOT_DIR} (Source: {source})")
logger.info("="*40)

IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".md", ".json", ".txt", ".html", ".css", ".java", ".c", ".cpp", ".rs", ".go"}

mcp = FastMCP("mcpv", log_level="DEBUG")

@mcp.tool()
def get_initial_context(force: bool = False) -> str:
    """[Smart Valve] Loads the codebase context via Repomix."""
    logger.info(f"Function 'get_initial_context' called. force={force}")
    
    allowed, msg = valve.check(force)
    logger.info(f"Valve check result: allowed={allowed}")
    
    if not allowed:
        return msg

    try:
        cmd = [
            "npx", "-y", "repomix",
            "--style", "xml",
            "--compress",
            "--remove-comments",
            "--output", "stdout"
        ]
        
        logger.info(f"▶️ Executing command: {' '.join(cmd)}")
        logger.info(f"   in Directory: {ROOT_DIR}")
        
        env = os.environ.copy()
        env["CI"] = "true"
        
        # [안전장치 추가] stdin=DEVNULL로 입력 대기 방지
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=(os.name == 'nt'),
            timeout=120, # 타임아웃 120초로 증가
            env=env,
            stdin=subprocess.DEVNULL 
        )
        
        logger.info(f"✅ Command finished. Return code: {result.returncode}")
        
        if result.returncode != 0:
            err_msg = f"Repomix Error (Code {result.returncode}): {result.stderr}"
            logger.error(err_msg)
            return err_msg
            
        output_len = len(result.stdout)
        logger.info(f"📝 Context fetched successfully! Length: {output_len} chars")
        
        return f"=== Vault Context ===\n{result.stdout}\n=== End Vault ==="
        
    except subprocess.TimeoutExpired:
        logger.error("⏰ Repomix timed out.")
        return "Error: Context fetching timed out."
        
    except Exception as e:
        logger.exception("❌ Unexpected error in get_initial_context")
        return f"Vault Error: {str(e)}"

# (use_upstream_tool, list_directory, read_file은 기존과 동일)
@mcp.tool()
async def use_upstream_tool(server_name: str, tool_name: str, args: dict = {}) -> str:
    try:
        session = await manager.get_session(server_name)
        res = await session.call_tool(tool_name, args)
        return "\n".join([c.text for c in res.content if c.type == "text"])
    except Exception as e:
        logger.error(f"Gateway Error: {e}")
        return f"Gateway Error: {e}"

@mcp.tool()
def list_directory(path: str = ".") -> str:
    logger.debug(f"list_directory called: {path}")
    full = (ROOT_DIR / path).resolve()
    if not str(full).startswith(str(ROOT_DIR)): return "⛔ Access Denied"
    if not full.exists(): return "Not found"
    
    out = []
    try:
        with os.scandir(full) as it:
            for e in it:
                if e.name in IGNORE_DIRS or e.name.startswith("."): continue
                if e.is_dir(): out.append(f"[DIR]  {e.name}/")
                elif e.is_file() and Path(e.name).suffix in ALLOWED_EXTENSIONS: out.append(f"[FILE] {e.name}")
    except Exception as e:
        return str(e)
    return "\n".join(sorted(out)) if out else "Empty"

@mcp.tool()
def read_file(path: str) -> str:
    logger.debug(f"read_file called: {path}")
    full = (ROOT_DIR / path).resolve()
    if not str(full).startswith(str(ROOT_DIR)): return "⛔ Access Denied"
    if full.suffix not in ALLOWED_EXTENSIONS: return f"⛔ File type {full.suffix} not allowed"
    try: return full.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return str(e)