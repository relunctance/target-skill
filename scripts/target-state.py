#!/usr/bin/env python3
"""
target-state — 目标状态管理脚本

用法：
  python target-state.py get                  # 读取当前目标状态
  python target-state.py set "目标描述"       # 设定新目标（需确认）
  python target-state.py status               # 简洁状态（一行）
  python target-state.py align               # 目标对齐检查
  python target-state.py log "操作" "详情"   # 追加变更日志
  python target-state.py update --field progress --value "描述"  # 更新进度
  python target-state.py add-subgoal "子目标标题" --priority P0   # 添加子目标
  python target-state.py list-subgoals       # 列举子目标
  python target-state.py done-subgoal 1     # 完成子目标
  python target-state.py remove-subgoal 1   # 删除子目标
  python target-state.py add-milestone "里程碑标题"  # 添加里程碑
  python target-state.py done-milestone 1   # 完成里程碑
  python target-state.py history            # 查看目标历史

状态文件：~/.hermes/profiles/baijie/.target-state.json
备份文件：~/.hermes/profiles/baijie/.target-state.json.bak
历史文件：~/.hermes/profiles/baijie/.target-history.json
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = Path.home() / ".hermes" / "profiles" / "baijie" / ".target-state.json"
BACKUP_FILE = STATE_FILE.with_suffix(".json.bak")
HISTORY_FILE = Path.home() / ".hermes" / "profiles" / "baijie" / ".target-history.json"


# ─── 工具函数 ───────────────────────────────────────────────────

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return _empty_state()


def _empty_state() -> dict:
    return {
        "goal": None,
        "phase": None,
        "createdAt": None,
        "lastUpdated": None,
        "progress": None,
        "milestones": [],
        "problems": [],
        "subGoals": [],
        "changeLog": [],
    }


def save_state(state: dict) -> None:
    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, BACKUP_FILE)
    state["lastUpdated"] = now()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _auto_log(action: str, detail: str = "") -> None:
    """自动追加 changeLog（内部用，所有写操作自动调用）"""
    state = load_state()
    state.setdefault("changeLog", []).append({
        "time": now(),
        "action": action,
        "detail": detail or action,
    })
    save_state(state)


def load_history() -> list:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []


def save_history(history: list) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _archive_current() -> dict:
    """归档当前目标到历史，返回归档前的状态"""
    state = load_state()
    if state.get("goal"):
        history = load_history()
        history.append({
            "archivedAt": now(),
            "goal": state["goal"],
            "phase": state["phase"],
            "createdAt": state["createdAt"],
            "completedAt": state.get("completedAt"),
            "lastUpdated": state["lastUpdated"],
            "progress": state["progress"],
        })
        save_history(history)
    return state


# ─── 子命令 ───────────────────────────────────────────────────

def cmd_get() -> str:
    state = load_state()
    if not state.get("goal"):
        return "📌 暂无进行中的目标"

    lines = [
        f"## 🎯 当前目标",
        f"**目标**: {state['goal']}",
        f"**状态**: {state['phase'] or '未知'}",
        f"**设定时间**: {state['createdAt'] or '未知'}",
        f"**最后更新**: {state['lastUpdated'] or '未知'}",
        f"**进度**: {state['progress'] or '暂无进度记录'}",
    ]

    subs = state.get("subGoals", [])
    if subs:
        lines.append("")
        lines.append("### 子目标")
        for sg in subs:
            e = "✅" if sg.get("status") == "done" else "⬜"
            lines.append(f"{e} [{sg['id']}] {sg.get('title', '')} ({sg.get('priority', '')})")

    ms = state.get("milestones", [])
    if ms:
        lines.append("")
        lines.append("### 里程碑")
        for m in ms:
            e = "🏁" if m.get("status") == "done" else "⬜"
            lines.append(f"{e} [{m['id']}] {m.get('title', '')}")

    logs = state.get("changeLog", [])
    if logs:
        lines.append("")
        lines.append("### 最近变更")
        for entry in logs[-3:]:
            lines.append(f"- [{entry.get('time', '')}] {entry.get('action', '')}: {entry.get('detail', '')}")

    return "\n".join(lines)


def cmd_set(goal: str, confirm: bool = False) -> str:
    state = load_state()
    if state.get("goal") and state["phase"] == "进行中" and not confirm:
        return (f"⚠️  当前已有进行中的目标：{state['goal']}\n\n"
                f"请先确认覆盖（加 --confirm）\n或回复「确认」执行覆盖。")

    # 只有在有未完成的目标时才归档（已完成/已放弃的已在对应命令里归档过了）
    if state.get("goal") and state.get("phase") == "进行中":
        _archive_current()

    state = _empty_state()
    state["goal"] = goal
    state["phase"] = "进行中"
    state["createdAt"] = now()
    state["progress"] = "目标刚设定，尚未开始推进"
    state["changeLog"] = [{"time": now(), "action": "目标设定", "detail": goal}]
    save_state(state)

    return (f"✅ 目标已设定\n\n"
            f"**目标**: {goal}\n"
            f"**状态**: 进行中\n"
            f"**时间**: {state['createdAt']}")


def cmd_status() -> str:
    state = load_state()
    if not state.get("goal"):
        return "📌 [目标] 暂无进行中的目标"

    subs = state.get("subGoals", [])
    done = sum(1 for s in subs if s.get("status") == "done")
    prog = (state.get("progress") or "")[:30]
    if len(prog) > 30:
        prog += "..."

    return f"🎯 [目标] {state['goal']} ({state['phase']}) | 子目标 {done}/{len(subs)} | {prog}"


def cmd_align() -> str:
    state = load_state()
    if not state.get("goal"):
        return "📌 暂无进行中的目标，无法进行对齐检查"

    subs = state.get("subGoals", [])
    ms = state.get("milestones", [])
    done_subs = sum(1 for s in subs if s.get("status") == "done")
    done_ms = sum(1 for m in ms if m.get("status") == "done")

    lines = [
        "## 🎯 目标对齐检查",
        f"**当前目标**: {state['goal']}",
        f"**进度**: {state['progress'] or '暂无记录'}",
        f"**子目标**: {done_subs}/{len(subs)} 完成",
        f"**里程碑**: {done_ms}/{len(ms)} 完成",
        "",
        "请选择：",
        "1. **继续** — 推进下一个子目标/里程碑",
        "2. **调整** — 修改目标或进度描述",
        "3. **暂停** — 暂时搁置",
        "4. **完成** — 标记目标达成",
        "5. **放弃** — 放弃当前目标",
    ]
    return "\n".join(lines)


def cmd_log(action: str, detail: str = "") -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标，无法记录变更"

    state.setdefault("changeLog", []).append({
        "time": now(),
        "action": action,
        "detail": detail or action,
    })
    save_state(state)
    return f"📝 已记录：[{now()}] {action}" + (f" — {detail}" if detail else "")


def cmd_update(field: str, value: str) -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    if field not in ("progress", "phase"):
        return f"❌ 不支持的字段：{field}（仅支持 progress/phase）"

    state[field] = value
    save_state(state)
    _auto_log(f"更新{field}", f"{field} → {value}")
    return f"✅ {field} 已更新为：{value}"


# ─── 子目标 CRUD ────────────────────────────────────────────────

def _next_subgoal_id(state: dict) -> int:
    ids = [sg["id"] for sg in state.get("subGoals", [])]
    return max(ids) + 1 if ids else 1


def cmd_add_subgoal(title: str, priority: str = "P1") -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    sg = {"id": _next_subgoal_id(state), "title": title, "priority": priority, "status": "pending"}
    state.setdefault("subGoals", []).append(sg)
    save_state(state)
    _auto_log("添加子目标", f"[{sg['id']}] {title} ({priority})")
    return f"✅ 子目标已添加\n\n**[{sg['id']}] {title}** ({priority})\n\n当前子目标：{len(state['subGoals'])}个"


def cmd_list_subgoals() -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    subs = state.get("subGoals", [])
    if not subs:
        return "📌 暂无子目标"

    lines = ["## 子目标列表"]
    for sg in subs:
        e = "✅" if sg.get("status") == "done" else "⬜"
        lines.append(f"{e} [{sg['id']}] {sg.get('title', '')} ({sg.get('priority', '')})")
    return "\n".join(lines)


def cmd_done_subgoal(sg_id: int) -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    for sg in state.get("subGoals", []):
        if sg["id"] == sg_id:
            sg["status"] = "done"
            sg["completedAt"] = now()
            save_state(state)
            _auto_log("完成子目标", f"[{sg_id}] {sg['title']}")
            done = sum(1 for s in state["subGoals"] if s.get("status") == "done")
            return f"✅ 子目标「{sg['title']}」已标记为完成\n\n子目标进度：{done}/{len(state['subGoals'])}"

    return f"❌ 未找到子目标 ID {sg_id}"


def cmd_remove_subgoal(sg_id: int) -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    subs = state.get("subGoals", [])
    for i, sg in enumerate(subs):
        if sg["id"] == sg_id:
            removed = subs.pop(i)
            save_state(state)
            _auto_log("删除子目标", f"[{sg_id}] {removed['title']}")
            return f"🗑️ 子目标「{removed['title']}」已删除"
    return f"❌ 未找到子目标 ID {sg_id}"


# ─── 里程碑 ────────────────────────────────────────────────────

def _next_milestone_id(state: dict) -> int:
    ids = [m["id"] for m in state.get("milestones", [])]
    return max(ids) + 1 if ids else 1


def cmd_add_milestone(title: str) -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    m = {"id": _next_milestone_id(state), "title": title, "status": "pending"}
    state.setdefault("milestones", []).append(m)
    save_state(state)
    _auto_log("添加里程碑", f"[{m['id']}] {title}")
    return f"✅ 里程碑已添加\n\n**[{m['id']}] {title}**\n\n当前里程碑：{len(state['milestones'])}个"


def cmd_list_milestones() -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    ms = state.get("milestones", [])
    if not ms:
        return "📌 暂无里程碑"

    lines = ["## 里程碑列表"]
    for m in ms:
        e = "🏁" if m.get("status") == "done" else "⬜"
        lines.append(f"{e} [{m['id']}] {m.get('title', '')}")
    return "\n".join(lines)


def cmd_done_milestone(m_id: int) -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    for m in state.get("milestones", []):
        if m["id"] == m_id:
            m["status"] = "done"
            m["completedAt"] = now()
            save_state(state)
            _auto_log("完成里程碑", f"[{m_id}] {m['title']}")
            done = sum(1 for x in state["milestones"] if x.get("status") == "done")
            return f"🏁 里程碑「{m['title']}」已标记为完成\n\n里程碑进度：{done}/{len(state['milestones'])}"

    return f"❌ 未找到里程碑 ID {m_id}"


# ─── 放弃 ─────────────────────────────────────────────────────

def cmd_abandon(reason: str = "") -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    abandoned_goal = state["goal"]
    # 先标记为已放弃，再归档
    state["phase"] = "已放弃"
    state["abandonedAt"] = now()
    state["abandonReason"] = reason
    save_state(state)
    _archive_current()
    empty = _empty_state()
    save_state(empty)

    return (f"⚠️ 目标已放弃\n\n"
            f"**目标**: {abandoned_goal}\n"
            f"**放弃原因**: {reason or '未说明'}\n"
            f"**时间**: {now()}")


# ─── 完成 ─────────────────────────────────────────────────────

def cmd_complete() -> str:
    state = load_state()
    if not state.get("goal"):
        return "❌ 暂无进行中的目标"

    completed_goal = state["goal"]
    # 先标记为已完成，再归档（归档时读走已完成状态）
    state["phase"] = "已完成"
    state["completedAt"] = now()
    save_state(state)
    _archive_current()  # 归档已完成状态
    empty = _empty_state()
    save_state(empty)  # 再清空

    return (f"🎉 目标已完成！\n\n"
            f"**目标**: {completed_goal}\n"
            f"**完成时间**: {now()}")


# ─── 历史 ─────────────────────────────────────────────────────

def cmd_history() -> str:
    history = load_history()
    if not history:
        return "📌 暂无目标历史"

    lines = ["## 📜 目标历史"]
    for i, h in enumerate(reversed(history[-10:])):  # 最近10条
        lines.append(f"\n### {i+1}. {h.get('goal', '')}")
        lines.append(f"**状态**: {h.get('phase', '')}")
        if h.get("createdAt"):
            lines.append(f"**设定**: {h['createdAt']}")
        if h.get("completedAt"):
            lines.append(f"**完成**: {h['completedAt']}")
        elif h.get("archivedAt"):
            lines.append(f"**归档**: {h['archivedAt']}")

    return "\n".join(lines)


# ─── 主入口 ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="target-state: 目标状态管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="cmd")

    # 基础命令
    sub.add_parser("get", help="读取当前目标状态")
    sub.add_parser("status", help="简洁状态（一行）")
    sub.add_parser("align", help="目标对齐检查")
    sub.add_parser("history", help="查看目标历史")

    p_set = sub.add_parser("set", help="设定新目标")
    p_set.add_argument("goal", help="目标描述")
    p_set.add_argument("--confirm", action="store_true", help="确认覆盖已有目标")

    p_log = sub.add_parser("log", help="追加变更日志")
    p_log.add_argument("action", help="操作类型")
    p_log.add_argument("detail", nargs="?", default="", help="详细描述")

    p_update = sub.add_parser("update", help="更新目标字段（progress/phase）")
    p_update.add_argument("--field", required=True, help="字段名")
    p_update.add_argument("--value", required=True, help="字段值")

    # 子目标命令
    p_add_sg = sub.add_parser("add-subgoal", help="添加子目标")
    p_add_sg.add_argument("title", help="子目标标题")
    p_add_sg.add_argument("--priority", default="P1", help="优先级（P0/P1/P2）")

    sub.add_parser("list-subgoals", help="列举子目标")

    p_done_sg = sub.add_parser("done-subgoal", help="完成子目标")
    p_done_sg.add_argument("id", type=int, help="子目标 ID")

    p_rm_sg = sub.add_parser("remove-subgoal", help="删除子目标")
    p_rm_sg.add_argument("id", type=int, help="子目标 ID")

    # 里程碑命令
    p_add_ms = sub.add_parser("add-milestone", help="添加里程碑")
    p_add_ms.add_argument("title", help="里程碑标题")

    sub.add_parser("list-milestones", help="列举里程碑")

    p_done_ms = sub.add_parser("done-milestone", help="完成里程碑")
    p_done_ms.add_argument("id", type=int, help="里程碑 ID")

    # 放弃/完成
    p_abandon = sub.add_parser("abandon", help="放弃目标")
    p_abandon.add_argument("reason", nargs="?", default="", help="放弃原因")

    sub.add_parser("complete", help="标记目标达成")

    args = parser.parse_args()

    if not args.cmd:
        print(cmd_get())
        return

    try:
        if args.cmd == "get":
            print(cmd_get())
        elif args.cmd == "set":
            print(cmd_set(args.goal, args.confirm))
        elif args.cmd == "status":
            print(cmd_status())
        elif args.cmd == "align":
            print(cmd_align())
        elif args.cmd == "log":
            print(cmd_log(args.action, args.detail))
        elif args.cmd == "update":
            print(cmd_update(args.field, args.value))
        elif args.cmd == "add-subgoal":
            print(cmd_add_subgoal(args.title, args.priority))
        elif args.cmd == "list-subgoals":
            print(cmd_list_subgoals())
        elif args.cmd == "done-subgoal":
            print(cmd_done_subgoal(args.id))
        elif args.cmd == "remove-subgoal":
            print(cmd_remove_subgoal(args.id))
        elif args.cmd == "add-milestone":
            print(cmd_add_milestone(args.title))
        elif args.cmd == "list-milestones":
            print(cmd_list_milestones())
        elif args.cmd == "done-milestone":
            print(cmd_done_milestone(args.id))
        elif args.cmd == "abandon":
            print(cmd_abandon(args.reason))
        elif args.cmd == "complete":
            print(cmd_complete())
        elif args.cmd == "history":
            print(cmd_history())
        else:
            parser.print_help()
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
