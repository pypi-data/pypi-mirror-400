import subprocess
import os
import platform
import shutil
from pathlib import Path


class CDDEngine:
    def __init__(self):
        self.home_ratel = Path.home() / ".ratel"
        self.bin_dir = self.home_ratel / "bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        # Identification of the platform and selection of the source binary
        system = platform.system()
        if system == "Windows":
            self.source_name = "ratel-windows-x64.exe"
            self.target_name = "ratel.exe"
        elif system == "Darwin":  # macOS
            self.source_name = "ratel-macos-x64"
            self.target_name = "ratel"
        else:  # Linux and others
            self.source_name = "ratel-linux-x64"
            self.target_name = "ratel"

        self.binary_path = self.bin_dir / self.target_name
        self._extract_binary()

    def _extract_binary(self):
        # localization of the binary inside the python package
        source_bin = Path(__file__).parent / "bin" / self.source_name

        if source_bin.exists():
            # Extraction/Update in ~/.ratel/bin/
            shutil.copy(source_bin, self.binary_path)

            # Apply execution rights for Unix
            if platform.system() != "Windows":
                os.chmod(self.binary_path, 0o755)
        else:
            print(f" Warning: Source binary {self.source_name} not found in package.")

    def init_project(self):
        # Calls 'ratel init' to create the tests/security/ directory structure
        print(f"🐾 Initializing Ratel workspace...")
        subprocess.run([str(self.binary_path), "init"], check=True)

    def execute_audit(self, target_url=None):
        # Standard path defined in Ratel's main.rs for Python
        scenario = "tests/ratel/security.ratel"

        print(f"🛡️ CDD Engine synchronized: {self.target_name}")
        try:
            # Execution of the extracted binary with the local scenario
            subprocess.run([str(self.binary_path), "run", scenario], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Audit failed with exit code: {e.returncode}")
        except FileNotFoundError:
            print(
                f"Error: Scenario file not found at {scenario}. Did you run cdd.init()?"
            )
