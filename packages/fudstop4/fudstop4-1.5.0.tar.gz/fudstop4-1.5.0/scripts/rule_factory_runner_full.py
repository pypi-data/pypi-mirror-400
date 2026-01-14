"""rule_factory_runner_full.py

Runs the expanded, diversified factory in a loop (useful while iterating).

Usage:
  python rule_factory_runner_full.py

Notes:
- Adjust `SLEEP_SECONDS` if you don't need continuous reruns.
- For a single run, call:
    python rule_factory_full.py --config rule_factory_full.yaml
"""

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "rule_factory_full.py"
CONFIG = HERE / "rule_factory.yaml"

SLEEP_SECONDS = 60


def main() -> None:
    if not SCRIPT.exists():
        raise FileNotFoundError(f"Missing {SCRIPT}")
    if not CONFIG.exists():
        raise FileNotFoundError(f"Missing {CONFIG}")

    while True:
        cmd = [sys.executable, str(SCRIPT), "--config", str(CONFIG)]
        print("\nRunning:", " ".join(cmd))
        subprocess.run(cmd, check=False)
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
