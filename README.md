# target-skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
[![version](https://img.shields.io/badge/version-3.1.0-green.svg)]()
[![category](https://img.shields.io/badge/category-productivity-blue.svg)]()
[![platforms](https://img.shields.io/badge/platforms-hermes-blue.svg)]()

> 目标追踪 + 抗偏移 — 设定目标后持续对齐，AI跑偏时主动纠正，歧义时让用户拍板

## 核心功能

### 基础功能

| 功能 | 说明 |
|------|------|
| **目标锁定** | 设定后持续追踪，每次回复前对齐 |
| **跑偏检测** | 立即识别偏移，列出对比分析 |
| **歧义确认** | 不自己猜，让用户选择方向 |
| **目标变化日志** | 每次调整记录原因，可回溯 |

### 强化功能（v3+）

| 功能 | 说明 |
|------|------|
| **验收标准门槛** | subTask 无 L3 验收标准时，拒绝执行 |
| **检查点机制** | 每个 subTask 完成后汇报，用户确认后才能继续 |
| **进度可见性** | 随时可查进度状态 |
| **抗偏移检查** | 每 3 个 subTask 做一次目标对齐检查 |
| **阻塞上报机制** | 遇到问题 AI 主动上报，不自行决定 |
| **中间交付物** | 每个 subTask 必须有可查看的交付物 |
| **可验证命令** | 验收标准必须包含可运行的验证命令 |
| **Rollback** | subTask 失败后可回滚到上一个可用状态 |
| **质量门禁** | milestone 切换时自动检查 lint + test |

## 触发条件

| 触发词 | 说明 |
|--------|------|
| `开始执行` / `执行追踪` | 从 task-split-skill 接管执行 |
| `设定目标` | 手动设定目标 |
| `当前进度` / `当前目标` | 查看进度 |
| `目标跑偏` / `AI跑偏` | 触发抗偏移检查 |
| `回滚` / `rollback` | 回滚到上一个可用状态 |

## 工作流程

```
task-split-skill 拆解完成
    ↓
用户说「开始执行」/「追踪目标」
    ↓
target-skill 读取 .task-split.json
    ↓
【前置检查】验收标准门槛（L3/L2/L1 分级）
    ↓
开始执行 subTask
    ↓
【检查点】subTask 完成 → 汇报 → 用户确认
    ↓
【抗偏移】每 3 个 subTask → 目标对齐检查
    ↓
【质量门禁】milestone 最后一个 subTask 完成 → lint + test 检查
    ↓
所有 subTask 完成 → 目标达成
```

## 验收标准分级（v3）

| 等级 | 定义 | 行为 |
|------|------|------|
| L3 可测试 | 有确定性命令 | ✅ 可执行 |
| L2 模糊 | 有条件但无法自动判断 | 🔴 拒绝，要求补充 |
| L1 无 | 无任何验收条件 | 🔴 拒绝，要求补充 |

## Rollback（v3.1）

subTask 失败后可回滚：

```
subTask N 执行失败
    ↓
【确认回滚范围】
列出 subTask N 的所有变更
    ↓
【执行回滚】
新增文件 → rm
修改文件 → git checkout HEAD --
    ↓
【继续或终止】
用户选择：重试 / 跳过 / 终止
```

## 质量门禁（v3.1）

milestone 切换时自动检查：

| 指标 | 命令 | 阈值 |
|------|------|------|
| Lint | `ruff check src/` | 0 errors |
| Test | `pytest tests/ -v` | 0 failures |

## 安装

```bash
hermes skills install https://github.com/relunctance/target-skill
```
