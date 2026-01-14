import subprocess
from pathlib import Path
from typing import Optional
import os

class NodeProcess:
    def __init__(self, session_id: str, auth_dir: Path):
        self.session_id = session_id
        self.auth_dir = auth_dir

        # Resolve paths RELATIVE TO THIS FILE (works in site-packages)
        self.node_dir = Path(__file__).resolve().parent / "node"
        self.index_js = self.node_dir / "index.js"

        self.process: Optional[subprocess.Popen] = None

    def _ensure_node_deps(self):
        """
        Ensure node_modules exists by running npm install once.
        """
        node_modules = self.node_dir / "node_modules"
        if node_modules.exists():
            return

        print("[INFO] Node dependencies not found. Installing...")

        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        try:
            subprocess.run(
            [npm_cmd, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            )
        except Exception:
            raise RuntimeError(
            "npm is not available on PATH. "
            "Please install Node.js (LTS) from https://nodejs.org/"
         )

        subprocess.run(
            [npm_cmd, "install"],
            cwd=str(self.node_dir),
            check=True,
        )

    def start(self) -> subprocess.Popen:
        self._ensure_node_deps()
        if not self.index_js.exists():
            raise RuntimeError(
                f"Node entry file not found: {self.index_js}\n"
                "The package installation may be corrupted."
            )

        cmd = [
            "node",
            str(self.index_js),
            self.session_id,
        ]

        # ---- DEBUG (keep for now) ----
        print("[DEBUG] Starting Node backend")
        print("[DEBUG] node_dir :", self.node_dir)
        print("[DEBUG] index_js :", self.index_js)
        print("[DEBUG] cmd      :", cmd)
        # ------------------------------

        self.process = subprocess.Popen(
            cmd,
            cwd=str(self.node_dir),   
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        return self.process
