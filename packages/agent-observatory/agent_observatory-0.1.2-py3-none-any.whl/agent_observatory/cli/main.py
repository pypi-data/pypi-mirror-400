import argparse
import json
import os
import time

from agent_observatory.internal.terminal import console, render_session_envelope


def process_file(path: str, tail: bool = False) -> None:
    if not os.path.exists(path):
        console.print(f"[error]File not found: {path}[/error]")
        return

    with open(path, encoding="utf-8") as f:
        # Initial read
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                render_session_envelope(payload)
            except Exception as e:
                console.print(f"[error]Failed to parse line: {e}[/error]")

        if tail:
            try:
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        render_session_envelope(payload)
                    except Exception as e:
                        console.print(f"[error]Failed to parse line: {e}[/error]")
            except KeyboardInterrupt:
                return


def main() -> None:
    parser = argparse.ArgumentParser(prog="obs-view")
    parser.add_argument("file", help="Path to JSONL log file")
    parser.add_argument("-t", "--tail", action="store_true", help="Tail the file")

    args = parser.parse_args()
    process_file(args.file, tail=args.tail)


if __name__ == "__main__":
    main()
