#!/usr/bin/env python3
"""
target-state — 目标状态管理脚本

提供 5 个子命令：
  python target-state.py get                  # 读取当前目标状态
  python target-state.py set <goal>         # 设定新目标（需确认）
  python target-state.py log <action> <detail>  # 追加变更日志
  python target-state.py align               # 目标对齐检查
  python target-state.py status              # 简洁状态汇报

状态文件：~/.hermes/profiles/baijie/.target-state.json
备份文件：~/.hermes/profiles/baijie/.target-state.json.bak
"""

import argparse
import json
import os
import sys
import shutil
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/profiles/baijie/.target-state.json")
BACKUP_FILE = STATE_FILE + ".bak"


# ─── 工具函数 ───────────────────────────────────────────────────

def load_state() -> dict:
    """读取状态文件，不存在则返回空结构"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "goal": None,
        "phase": None,
        "createdAt": None,
        "lastUpdated": None,
        "progress": None,
        "milestones": [],
        "problems": [],
        "subGoals": [],
        "changeLog": []
    }


def save_state(state: dict) -> None:
    """写入状态文件（先备份）"""
    # 备份
    if os.path.exists(STATE_FILE):
        shutil.copy2(STATE_FILE, BACKUP_FILE)

    state["lastUpdated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ─── 子命令：get ─────────────────────────────────────────────────

def cmd_get() -> str:
    """读取当前目标状态"""
    state = load_state()

    if not state["goal"]:
        return "📌 暂无进行中的目标"

    lines = [
        f"## 🎯 当前目标",
        f"**目标**: {state['goal']}",
        f"**状态**: {state['phase'] or '未知'}",
        f"**设定时间**: {state['createdAt'] or '未知'}",
        f"**最后更新**: {state['lastUpdated'] or '未知'}",
        f"**进度**: {state['progress'] or '暂无进度记录'}",
    ]

    if state["subGoals"]:
        lines.append("")
        lines.append("### 子目标")
        for sg in state["subGoals"]:
            emoji = "✅" if sg.get("status") == "done" else "⬜"
            lines.append(f"{emoji} {sg.get('title', '')} ({sg.get('priority', '')})")

    if state["changeLog"]:
        lines.append("")
        lines.append("### 最近变更")
        for entry in state["changeLog"][-3:]:
            lines.append(f"- [{entry.get('time', '')}] {entry.get('action', '')}: {entry.get('detail', '')}")

    return "\n".join(lines)


# ─── 子命令：set ─────────────────────────────────────────────────

def cmd_set(goal: str, confirm: bool = False) -> str:
    """设定新目标（需确认）"""
    if not confirm:
        state = load_state()
        if state["goal"] and state["phase"] == "进行中":
            return f"⚠️  当前已有进行中的目标：{state['goal']}\n\n请先确认覆盖（加 --confirm）\n或回复「确认」执行覆盖。"

    state = load_state()
    # 保留变更日志和里程碑，清空其余字段，重新初始化
    old_goal = state["goal"]
    state["goal"] = goal
    state["phase"] = "进行中"
    state["createdAt"] = now()
    state["lastUpdated"] = now()
    state["progress"] = "目标刚设定，尚未开始推进"
    state["subGoals"] = []
    state["problems"] = []
    state["milestones"] = []

    save_state(state)

    msg = f"✅ 目标已设定\n\n**目标**: {goal}\n**状态**: 进行中\n**时间**: {state['createdAt']}"
    if old_goal:
        msg += f"\n\n（上一目标「{old_goal}」已归档）"
    return msg


# ─── 子命令：log ─────────────────────────────────────────────────

def cmd_log(action: str, detail: str = "") -> str:
    """追加变更日志"""
    state = load_state()

    if not state["goal"]:
        return "❌ 暂无进行中的目标，无法记录变更"

    entry = {
        "time": now(),
        "action": action,
        "detail": detail or action
    }
    state.setdefault("changeLog", []).append(entry)
    save_state(state)

    return f"📝 已记录：[{entry['time']}] {action}" + (f" — {detail}" if detail else "")


# ─── 子命令：align ────────────────────────────────────────────────

def cmd_align() -> str:
    """目标对齐检查"""
    state = load_state()

    if not state["goal"]:
        return "📌 暂无进行中的目标，无法进行对齐检查"

    lines = [
        "## 🎯 目标对齐检查",
        f"**当前目标**: {state['goal']}",
        f"**进度**: {state['progress'] or '暂无记录'}",
        f"**状态**: {state['phase']}",
        "",
        "请选择：",
        "1. **继续** — 推进下一个子目标",
        "2. **调整** — 修改目标或进度描述",
        "3. **暂停** — 暂时搁置",
        "4. **完成** — 标记目标达成",
    ]

    return "\n".join(lines)


# ─── 子命令：status ──────────────────────────────────────────────

def cmd_status() -> str:
    """简洁状态汇报（一行）"""
    state = load_state()

    if not state["goal"]:
        return "📌 [目标] 暂无进行中的目标"

    subs = state.get("subGoals", [])
    done = sum(1 for s in subs if s.get("status") == "done")
    total = len(subs)

    progress = state.get("progress", "")
    if len(progress) > 30:
        progress = progress[:30] + "..."

    return f"🎯 [目标] {state['goal']} ({state['phase']}) | 子目标 {done}/{total} | {progress}"


# ─── 子命令：update ──────────────────────────────────────────────

def cmd_update(field: str = "", value: str = "", subgoal_id: int = None, subgoal_status: str = "") -> str:
    """更新目标字段或子目标状态"""
    state = load_state()

    if not state["goal"]:
        return "❌ 暂无进行中的目标"

    if subgoal_id is not None and subgoal_status:
        # 更新子目标状态
        subs = state.get("subGoals", [])
        for sg in subs:
            if sg.get("id") == subgoal_id:
                sg["status"] = subgoal_status
                if subgoal_status == "done":
                    sg["completedAt"] = now()
                save_state(state)
                return f"✅ 子目标「{sg.get('title', subgoal_id)}」已标记为 {subgoal_status}"
        return f"❌ 未找到子目标 ID {subgoal_id}"

    if field and value:
        if field == "progress":
            state["progress"] = value
        elif field == "phase":
            state["phase"] = value
        else:
            return f"❌ 不支持的字段：{field}"
        save_state(state)
        return f"✅ {field} 已更新为：{value}"

    return "❌ 请指定 --field 和 --value"


# ─── 主入口 ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="target-state: 目标状态管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python target-state.py get
  python target-state.py set "完成 hawk-memory v2 开发"
  python target-state.py log "完成里程碑" "KR3.5 已交付"
  python target-state.py align
  python target-state.py status
  python target-state.py update --field progress --value "已完成 P0，正在做 P1"
  python target-state.py update --subgoal-id 1 --subgoal-status done
"""
    )

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("get", help="读取当前目标状态")
    sub.add_parser("status", help="简洁状态（一行）")
    sub.add_parser("align", help="目标对齐检查")

    p_set = sub.add_parser("set", help="设定新目标")
    p_set.add_argument("goal", help="目标描述")
    p_set.add_argument("--confirm", action="store_true", help="确认覆盖已有目标")

    p_log = sub.add_parser("log", help="追加变更日志")
    p_log.add_argument("action", help="操作类型")
    p_log.add_argument("detail", nargs="?", default="", help="详细描述")

    p_update = sub.add_parser("update", help="更新目标字段")
    p_update.add_argument("--field", default="", help="字段名（progress/phase）")
    p_update.add_argument("--value", default="", help="字段值")
    p_update.add_argument("--subgoal-id", type=int, default=None, help="子目标 ID")
    p_update.add_argument("--subgoal-status", default="", help="子目标状态（done/pending/active）")

    args = parser.parse_args()

    if not args.cmd:
        # 无子命令时，默认 get
        print(cmd_get())
        return

    try:
        if args.cmd == "get":
            print(cmd_get())
        elif args.cmd == "set":
            print(cmd_set(args.goal, args.confirm))
        elif args.cmd == "log":
            print(cmd_log(args.action, args.detail))
        elif args.cmd == "align":
            print(cmd_align())
        elif args.cmd == "status":
            print(cmd_status())
        elif args.cmd == "update":
            print(cmd_update(args.field, args.value, args.subgoal_id, args.subgoal_status))
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
