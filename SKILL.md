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
version: "3.1.0"
platforms: all
depends_on:
  - task-split-skill  # https://github.com/relunctance/task-split-skill
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
- `拆解任务` → [task-split-skill](https://github.com/relunctance/task-split-skill)
- `评审计划` → [plan-review-skill](https://github.com/relunctance/plan-review-skill)

---

## 三种启动方式

### 方式 1：从 .task-split.json 接管（推荐）

```
[task-split-skill](https://github.com/relunctance/task-split-skill) 拆解完成，写入 .task-split.json
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
[plan-review-skill](https://github.com/relunctance/plan-review-skill) 批准后写 .target-trigger
    ↓
用户说「追踪目标」
    ↓
target-skill 检测到 .target-trigger
    ↓
检查是否有 .task-split.json
    ├── 有 → 读取并开始追踪
    └── 无 → 提示用户「请先用 [task-split-skill](https://github.com/relunctance/task-split-skill) 拆解」
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
提示用户「请先用 [task-split-skill](https://github.com/relunctance/task-split-skill) 拆解」
```

### 与 PLAN skill 的关系

```
[PLAN skill](https://github.com/relunctance/plan-skill) 生成 docs/PLAN.md
    ↓
[plan-review-skill](https://github.com/relunctance/plan-review-skill) 评审
    ↓
[task-split-skill](https://github.com/relunctance/task-split-skill) 拆解
    ↓
target-skill 追踪
```

---

## 强化执行（v3 新增）

### 强化项 1：验收标准门槛

**规则**：subTask 没有可测试的验收标准，拒绝执行。

#### 验收标准分级

| 等级 | 定义 | 例子 | 行为 |
|------|------|------|------|
| L3 可测试 | 有确定性命令，返回明确结果 | `pytest tests/ -v` 返回 PASSED | ✅ 可执行 |
| L2 模糊 | 有验收条件但无法自动判断 | 「配置合理」「代码规范」 | 🔴 拒绝，要求补充 |
| L1 无 | 无任何验收条件 | 「完成开发」「完善功能」 | 🔴 拒绝，要求补充 |

#### 判断 SOP

```
收到 subTask
    ↓
检查验收标准：
├── L3（可测试命令）→ ✅ 进入执行
├── L2（模糊）→ 🔴 拒绝执行，输出：
│   「验收标准【{模糊内容}】不可测试。请补充具体命令或可验证的指标。」
│   「建议修改为：ruff check src/ 返回 0 errors」
└── L1（无）→ 🔴 拒绝执行，输出：
    「subTask【{task}】缺少验收标准。请补充后再执行。」
```

#### 示例

| subTask | 验收标准 | 判定 | 行为 |
|---------|---------|------|------|
| 配置 ruff lint | `ruff check src/` 返回 0 errors | L3 | ✅ 执行 |
| 配置合理 | 无 | L1 | 🔴 拒绝，要求补充 |
| 代码规范 | 有条件但无法自动判断 | L2 | 🔴 拒绝，要求补充 |

---

### 强化项 2：检查点机制

**规则**：每个 subTask 完成后，必须汇报并获得确认，才能执行下一个。

#### 检查点 SOP

```
subTask N 完成
    ↓
【汇报】
产出物：{文件/命令/文档}
验收标准：{原定标准}
实际结果：{执行结果}
状态：✅ 完成 / ⚠️ 有偏差 / 🔴 失败
    ↓
【等待确认】
用户确认 → 进入下一个 subTask
用户拒绝 → 修复后重新汇报
```

#### 汇报模板

```markdown
## subTask 汇报：{subTask ID}

**任务**：{task}
**验收标准**：{原定标准}

**产出物**：
- `{path}`：{说明}（状态：✅存在 | ❌缺失）
- `{path}`：{说明}（状态：✅存在 | ❌缺失）

**执行结果**：
```
{命令输出}
```

**状态**：✅ 完成 | ⚠️ 有偏差 | 🔴 失败

【等待确认】请确认是否可以进入下一个 subTask。
```

---

### 强化项 3：进度可见性

**规则**：定期输出进度状态，用户随时可查。

#### 进度汇报模板

```markdown
## 进度汇报

**目标**：{goal}
**锚点**：{anchor}
**进度**：{N}/{total} subTasks 完成（{percent}%）
**状态**：进行中 | 阻塞 | 暂停

**已完成**：
- ✅ {subTask ID}：{task}
- ✅ {subTask ID}：{task}

**当前**：{subTask ID} 执行中

**阻塞**：无 | {描述}

**预计剩余**：约 {时间}
```

#### 触发时机

| 时机 | 是否汇报 |
|------|---------|
| 用户询问「进度」 | ✅ |
| 每个 subTask 完成 | ✅ |
| 每 20 分钟 | ✅ |
| 遇到阻塞 | ✅ |
| 目标变更 | ✅ |

---

### 强化项 4：抗偏移检查

**规则**：每完成 3 个 subTask，做一次目标对齐检查。

#### 抗偏移 SOP

```
已完成 N 个 subTask（N % 3 == 0）
    ↓
【目标对齐检查】
当前目标：{goal}
已完成：{列表}
与目标的关联：{描述}
偏离度：低 / 中 / 高
    ↓
【判断】
├── 偏离度低 → 继续执行
├── 偏离度中 → 输出警告，继续执行
└── 偏离度高 → 暂停，询问用户
```

#### 目标对齐检查模板

```markdown
## 目标对齐检查

**已执行**：{N} 个 subTasks
**当前目标**：{goal}

**已完成 vs 目标**：
| subTask | 任务 | 与目标的关联 |
|---------|------|-------------|
| M1-1 | 实现 team create | ✅ 直接相关 |
| M1-2 | 实现 flow advance | ✅ 直接相关 |
| M1-3 | 优化文档 | ⚠️ 弱相关 |

**偏离度**：低 | 中 | 高

{如果偏离度高：}
**警告**：当前执行内容与目标偏离。请确认：
1. 继续执行当前 subTask？
2. 调整目标？
3. 暂停等待指令？
```

#### 偏离度判断标准

| 偏离度 | 定义 | 例子 |
|--------|------|------|
| 低 | 已完成与目标直接相关 | M1-1~M1-3 都是 M1 核心功能 |
| 中 | 部分与目标相关 | M1-1~M1-2 核心，M1-3 开始做文档 |
| 高 | 已完成与目标无关或反向 | M1-1 是核心，但开始做 M3 的内容 |

---

### 强化项 5：阻塞上报机制

**规则**：AI 遇到问题不能自行决定，必须上报用户。

#### 阻塞类型

| 类型 | 例子 | 行为 |
|------|------|------|
| 决策阻塞 | 需要用户拍板 | 暂停，上报 |
| 依赖阻塞 | 外部依赖未就绪 | 暂停，上报 |
| 技术阻塞 | error/exception 无法自行解决 | 暂停，上报 |
| 模糊阻塞 | 不确定是否正确 | 询问，上报 |

#### 阻塞上报模板

```markdown
## ⚠️ 阻塞报告

**subTask**：{subTask ID}
**阻塞类型**：{类型}

**问题描述**：
{详细描述}

**已尝试的方案**：
1. {方案1} → {结果}
2. {方案2} → {结果}

**可能的解决方案**：
1. {方案A} → {优缺点}
2. {方案B} → {优缺点}

**请决策**：请选择方案或提供指令。
```

#### 禁止行为

- ❌ AI 遇到 error 不上报，自行加 try-catch 掩盖
- ❌ AI 遇到决策模糊自行决定
- ❌ AI 遇到依赖缺失自行降级

---

### 强化项 6：中间过程交付物

**规则**：每个 subTask 必须有可查看的交付物。

#### 交付物类型

| subTask 类型 | 交付物要求 |
|-------------|-----------|
| 代码实现 | `.py` / `.ts` / `.go` 等源文件，lint 通过 |
| 配置 | `.toml` / `.yaml` / `.json` 等，语法正确 |
| 文档 | `.md` / `.txt` 等，内容非空 |
| 测试 | `test_*.py` 等，可运行 |
| CLI 命令 | 帮助文档或 man page |

#### 交付物检查 SOP

```
subTask 完成后
    ↓
检查交付物是否存在：
├── 存在 → 记录到 changeLog
└── 不存在 → 🔴 标记为失败
    「subTask【{task}】声称完成但无交付物。状态：失败」
```

#### 交付物记录模板

```markdown
**交付物**：
- `{path}`：{说明}（状态：✅存在 | ❌缺失）
- `{path}`：{说明}（状态：✅存在 | ❌缺失）
```

---

### 强化项 7：可验证命令

**规则**：每个验收标准必须包含人类可直接运行的命令。

#### 可验证命令分级

| 等级 | 定义 | 例子 | 行为 |
|------|------|------|------|
| 强 | 命令返回确定性结果 | `pytest tests/ -v` 返回 PASSED | ✅ 执行 |
| 弱 | 命令存在但结果不确定 | `ruff check src/` 可能返回 warning | ⚠️ 可执行，建议补充 |
| 无 | 无命令 | 「代码规范」 | 🔴 拒绝 |

#### 可验证命令示例

| subTask | 验收标准 | 判定 | 建议 |
|---------|---------|------|------|
| 配置 ruff | `ruff check src/` 返回 0 errors | 强 | ✅ 执行 |
| 编写测试 | `pytest tests/` 能运行 | 强 | ✅ 执行 |
| 代码规范 | 有规范文档 | 弱 | ⚠️ 补充命令 |
| 完善功能 | 无 | 无 | 🔴 拒绝 |

---

## Rollback SOP（v3 新增）

**触发条件**：subTask N 执行失败或用户要求回滚。

### Rollback 判断

```
subTask N 执行失败
    ↓
【检查是否可以回滚】
├── 有可回滚的变更（文件/配置）→ 执行回滚
└── 无可回滚的变更（纯逻辑失败）→ 标记 blocked，上报
```

### 回滚类型与方式

| 类型 | 场景 | 回滚方式 |
|------|------|---------|
| 文件删除 | subTask 新增了文件 | `rm {file}` 或 `git checkout HEAD -- {file}` |
| 文件修改 | subTask 修改了现有文件 | `git checkout HEAD -- {file}` |
| 配置变更 | subTask 修改了配置 | 恢复备份或手动改回 |
| 依赖安装 | `pip install` 等 | `pip uninstall {package}` |

### Rollback 执行流程

```
【确认回滚范围】
列出 subTask N 的所有变更
    ↓
【执行回滚】
对于每个变更：
├── 新增文件 → rm
├── 修改文件 → git checkout HEAD --
└── 配置变更 → 手动恢复
    ↓
【更新状态】
.subTask N 状态 → pending
.target-state.json lastUpdated → 当前时间
.changeLog → 记录回滚
    ↓
【继续或终止】
用户决定：
1. 重试 subTask N
2. 跳过 subTask N
3. 终止 milestone
```

### Rollback 汇报模板

```markdown
## 🔄 Rollback 汇报

**subTask**：{subTask ID}
**回滚原因**：{失败原因 / 用户要求}

**回滚变更**：
- `{file}`：新增文件 → 已删除
- `{file}`：修改文件 → 已从 git 恢复

**当前状态**：
- {subTask ID}：pending
- milestone {M}：active

**下一步**：请选择：
1. 重试 {subTask ID}
2. 跳过 {subTask ID}
3. 终止 milestone
```

---

## 质量门禁 SOP（v3 新增）

**触发条件**：milestone N 的最后一个 subTask 完成。

### 质量门禁检查

```
milestone N 最后一个 subTask 完成
    ↓
【质量门禁检查】
├── ruff lint src/ → 0 errors
├── pytest tests/ → 0 failures
└── （其他质量指标，如有）
    ↓
【判断】
├── 全部通过 → ✅ 进入下一 milestone
└── 有失败 → 🔴 阻塞
    「质量门禁未通过。请修复后再继续。」
```

### 质量门禁指标

| 指标 | 命令 | 阈值 |
|------|------|------|
| Lint | `ruff check src/` | 0 errors |
| Test | `pytest tests/ -v` | 0 failures |
| Type check（可选） | `mypy src/` | 0 errors |

### 质量门禁失败汇报模板

```markdown
## 🔴 质量门禁未通过

**milestone**：{M}
**检查时间**：{timestamp}

**失败项**：
| 指标 | 命令 | 实际结果 | 期望 |
|------|------|---------|------|
| Lint | `ruff check src/` | 5 errors | 0 errors |
| Test | `pytest tests/ -v` | 2 failed | 0 failures |

**阻塞**：milestone {M} 状态 → blocked

**下一步**：请修复上述问题，然后说「重新检查质量门禁」。
```

### 质量门禁通过汇报模板

```markdown
## ✅ 质量门禁通过

**milestone**：{M}
**检查时间**：{timestamp}

**检查项**：
| 指标 | 结果 |
|------|------|
| ruff lint | ✅ 0 errors |
| pytest | ✅ 0 failures |

**下一步**：milestone {M} 完成，进入 milestone {M+1}。
```

---

## subTask 完整执行流程（v3）

```
subTask N 开始
    ↓
【前置检查】
├── 验收标准存在？→ 无 → 🔴 拒绝执行
├── 验收标准可测试？→ 模糊/无 → 🔴 拒绝执行
└── 验收标准可测试 → ✅ 进入执行
    ↓
【执行】
执行 subTask，产出交付物
    ↓
【后置检查】
├── 交付物存在？→ 无 → 🔴 标记失败
├── 验收标准满足？→ 否 → ⚠️ 汇报偏差
└── 验收标准满足 → ✅ 汇报完成
    ↓
【检查点】
汇报 → 等待用户确认
    ↓
【抗偏移检查】
已完成 N 个（每 3 个）→ 目标对齐检查
    ↓
subTask N+1 开始
```

---

## 版本字段

详细格式定义见 `docs/schemas.md`。

| 文件 | 版本字段 | 位置 |
|------|---------|------|
| `.target-state.json` | `schemaVersion` | JSON 顶层 |

---

## 安装

```bash
git clone https://github.com/relunctance/target-skill.git ~/repos/target-skill
```
