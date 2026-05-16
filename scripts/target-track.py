#!/usr/bin/env python3
"""
target-track.py — 目标追踪状态读写

用法：
  python3 target-track.py read [项目路径]      # 读取当前状态
  python3 target-track.py write [项目路径]      # 写入状态（从 stdin 读 JSON）
  python3 target-track.py trigger [项目路径]    # 检查 trigger，返回 planFile
"""

import json
import sys
from pathlib import Path


def read_state(project: Path) -> dict | None:
    f = project / ".target-state.json"
    if f.exists():
        return json.loads(f.read_text())
    return None


def write_state(project: Path, data: dict) -> None:
    (project / ".target-state.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2)
    )


def get_trigger(project: Path) -> dict | None:
    f = project / ".target-trigger"
    if f.exists():
        return json.loads(f.read_text())
    return None


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["read"]
    project = Path(args[0]) if args else Path.cwd()

    if cmd == "read":
        result = read_state(project)
        print(json.dumps(result, ensure_ascii=False, indent=2) if result else "null")
    elif cmd == "write":
        data = json.load(sys.stdin)
        write_state(project, data)
    elif cmd == "trigger":
        result = get_trigger(project)
        print(json.dumps(result, ensure_ascii=False, indent=2) if result else "null")
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        sys.exit(1)
