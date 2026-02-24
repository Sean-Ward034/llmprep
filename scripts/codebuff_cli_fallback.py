"""Codebuff CLI fallback wrapper around llmprep ingest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run llmprep ingest as a Codebuff-friendly fallback wrapper.")
    parser.add_argument("--path", required=True, help="Input file or directory")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--print", action="store_true", dest="do_print", help="Print result JSON")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Pass --json to llmprep")
    args = parser.parse_args()

    cmd = ["llmprep", "ingest", args.path, "--out", args.out, "--force"]
    if args.json_output:
        cmd.append("--json")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if args.do_print:
        payload = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
        print(json.dumps(payload, indent=2))
    else:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

