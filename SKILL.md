---
name: target-skill
description: 目标追踪 + 抗偏移 — 设定目标后持续对齐，AI跑偏时主动纠正，歧义时让用户确认
triggers:
  - 设定目标
  - 目标跑偏
  - AI跑偏
  - 追踪目标
  - 目标执行
  - 保持目标
  - 目标偏离
  - 纠正AI
  - 发现更大目标
  - 目标变化
  - 设定小目标
  - 添加子目标
  - 继续目标
  - 批准了规划
  - 开始执行
  - 执行追踪
  - 当前进度
  - 有什么被阻塞了
  - 切换到执行模式
  - 回顾目标
  - 继续追踪目标
  - 我的目标是什么
  - 你的目标
  - 当前目标
  - 我的当前目标
category: productivity
author: relunctance
created: 2026-05-15
updated: 2026-05-17
version: "2.1.0"
platforms: all
depends_on:
  - task-split-skill
tags:
  - goal
  - tracking
  - focus
  - productivity
  - anti-drift
---

# target-skill

> 让 AI 始终围绕目标工作，跑偏时主动纠正，歧义时让用户拍板

---

## 核心原则

### 第一原则：目标永远优先

每次回复前，先问自己：**这个回复是否在推进目标？**

### 第二原则：用户有最终决策权

歧义、偏移、目标变化 — 不自己猜，让用户选择。

### 第三原则：必须用户确认才能更新状态

**所有目标状态变更必须经过用户明确确认，AI 不得擅自更新。**

---

## 触发条件

### 每次新对话开始时（必须执行）

```markdown
## 🎯 目标检查

你好！请问是否有进行中的目标需要继续追踪？

1. **有目标** — 请告诉我项目路径或目标名称，我读取 `.target-state.json` 恢复状态
2. **新目标** — 请描述你的目标，我来拆解和追踪
3. **无目标** — 好的，随时可以告诉我
```

### 用户主动触发

| 触发词 | 说明 |
|--------|------|
| `追踪目标` / `开始执行` | 从 task-split-skill 接管 |
| `设定目标` | 手动设定目标 |
| `当前进度` / `当前目标` | 查看进度 |

**不触发：**
- `制定计划` → PLAN skill
- `拆解任务` → task-split-skill
- `评审计划` → plan-review-skill

---

## 三种启动方式

### 方式 1：从 .task-split.json 接管（推荐）

```
task-split-skill 拆解完成，写入 .task-split.json
    ↓
用户说「开始执行」/「追踪目标」
    ↓
target-skill 读取 .task-split.json
    ↓
转换为 .target-state.json
    ↓
开始追踪
```

### 方式 2：从 .target-trigger 接管

```
plan-review-skill 批准后写 .target-trigger
    ↓
用户说「追踪目标」
    ↓
target-skill 检测到 .target-trigger
    ↓
检查是否有 .task-split.json
    ├── 有 → 读取并开始追踪
    └── 无 → 提示用户「请先用 task-split-skill 拆解」
```

### 方式 3：手动设定目标

```
用户说「设定目标」
    ↓
按现有 SOP 设定目标
    ↓
写入 .target-state.json
    ↓
开始追踪
```

---

### .task-split.json 格式（task-split-skill 输出）

```json
{
  "version": "1.0",
  "goal": "{项目目标}",
  "source": "PLAN.md",
  "createdAt": "YYYY-MM-DDTHH:mm:ss+08:00",
  "milestones": [
    {
      "id": "M1",
      "title": "{标题}",
      "status": "pending",
      "subTasks": [
        {
          "id": "M1-1",
          "title": "{任务}",
          "status": "pending",
          "priority": "P0",
          "acceptanceCriteria": "{验收标准}"
        }
      ]
    }
  ]
}
```

### .target-state.json 格式（target-skill 使用）

```json
{
  "goal": "项目愿景",
  "phase": "active",
  "source": "task-split",
  "createdAt": "YYYY-MM-DDTHH:mm:ss+08:00",
  "lastUpdated": "YYYY-MM-DDTHH:mm:ss+08:00",
  "milestones": [
    {
      "id": "M1",
      "title": "里程碑标题",
      "status": "active",
      "completedAt": null,
      "subTasks": [
        {
          "id": "M1-1",
          "title": "子任务标题",
          "status": "done",
          "completedAt": "YYYY-MM-DDTHH:mm:ss+08:00"
        }
      ]
    }
  ],
  "changeLog": []
}
```

### .task-split.json → .target-state.json 转换规则

| .task-split.json | .target-state.json |
|-----------------|-------------------|
| `goal` | `goal` |
| `source: "PLAN.md"` | `source: "task-split"` |
| `milestones[].id` | `milestones[].id` |
| `milestones[].title` | `milestones[].title` |
| `milestones[].status` | `milestones[].status`（默认 `pending`） |
| `subTasks[].id` | `subTasks[].id` |
| `subTasks[].title` | `subTasks[].title` |
| `subTasks[].status` | `subTasks[].status`（默认 `pending`） |
| `subTasks[].priority` | （不转换，优先级在追踪时使用） |
| `subTasks[].acceptanceCriteria` | （不转换，验收标准在追踪时使用） |

### 状态字段说明

| 字段 | 说明 |
|------|------|
| `source` | `"task-split"` 或 `"manual"` |
| `milestones[].status` | `pending` / `active` / `done` |
| `subTasks[].status` | `pending` / `active` / `blocked` / `done` |

### 状态转换规则

```
milestone.status:
  pending → active（第一个 subTask 开始）
  active → done（所有 subTask done）
  active → blocked（所有 subTask blocked）

subTask.status:
  pending → active（开始执行）
  active → done（完成）
  active → blocked（被依赖阻塞）
  blocked → active（依赖完成）
```

---

## 每次回复前的对齐检查

```
目标追踪检查:
[ ] 这个回复是否推进当前目标？
[ ] 是否有新的偏移迹象？
[ ] P0 阻塞问题有新进展吗？
[ ] 是否遇到新的问题/障碍？
[ ] 健康度是否有下降？

如果任何一项异常 → 先处理异常，再继续
```

### 健康度评分

| 维度 | 权重 |
|------|------|
| 进度（子目标完成率） | 25% |
| P0阻塞（无P0=25，未解决P0=0） | 25% |
| 偏移风险（无偏移=25，有偏移=0） | 25% |
| 时间透支（未超=25，超时扣分） | 25% |

| 等级 | 分数 |
|------|------|
| 🟢 健康 | 80-100 |
| 🟡 警告 | 50-79 |
| 🔴 危险 | 0-49 |

---

## 与其他 Skill 的关系

### 与 task-split-skill 的关系（主要输入来源）

```
task-split-skill 拆解完成
    ↓
输出 milestone + subTask
    ↓
target-skill 接收
    ↓
写入 .target-state.json
    ↓
开始追踪
```

### 与 plan-review-skill 的关系

```
plan-review-skill 批准时写 .target-trigger
    ↓
target-skill 读取 .target-trigger
    ↓
发现无 milestone + subTask
    ↓
提示用户「请先用 task-split-skill 拆解」
```

### 与 PLAN skill 的关系

```
PLAN skill 生成 docs/PLAN.md
    ↓
plan-review-skill 评审
    ↓
task-split-skill 拆解
    ↓
target-skill 追踪
```

---

## 版本字段

| 文件 | 版本字段 | 位置 |
|------|---------|------|
| `.target-state.json` | `schemaVersion` | JSON 顶层 |

---

## 安装

```bash
git clone https://github.com/relunctance/target-skill.git ~/repos/target-skill
```
