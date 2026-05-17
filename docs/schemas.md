# Schema 版本契约

> 所有 Skill 的输出格式版本在此定义。版本不匹配时提示用户，不卡住。

---

## 一、文件清单

| 文件 | 创建者 | 消费者 | 版本字段 |
|------|--------|--------|---------|
| `docs/PLAN.md` | PLAN skill | plan-review-skill, task-split-skill | `version` |
| `.target-trigger` | plan-review-skill | target-skill | `version` |
| `.task-split.json` | task-split-skill | target-skill | `version` |
| `.target-state.json` | target-skill | target-skill | `schemaVersion` |

---

## 二、文件格式

### 2.1 docs/PLAN.md

```yaml
---
status: draft | approved | archived
version: "1.0"
author: {user_name}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
---
```

**章节**：
- `# 项目愿景`
- `# 需求约束`（含 MVP、技术约束、限制条件）
- `# 里程碑`（表格）
- `# 交付物`（表格）
- `# 风险预判`（表格）

---

### 2.2 .target-trigger

```json
{
  "version": "1.0",
  "planFile": "docs/PLAN.md",
  "approvedAt": "{YYYY-MM-DDTHH:mm:ss+08:00}",
  "approvedBy": "{user_name}",
  "goal": "{项目愿景}"
}
```

---

### 2.3 .task-split.json

```json
{
  "version": "1.0",
  "goal": "{项目目标}",
  "source": "docs/PLAN.md",
  "createdAt": "{YYYY-MM-DDTHH:mm:ss+08:00}",
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

---

### 2.4 .target-state.json

```json
{
  "goal": "{项目愿景}",
  "phase": "active | completed | abandoned",
  "source": "manual | task-split",
  "schemaVersion": "1.0",
  "createdAt": "{YYYY-MM-DDTHH:mm:ss+08:00}",
  "lastUpdated": "{YYYY-MM-DDTHH:mm:ss+08:00}",
  "milestones": [
    {
      "id": "M1",
      "title": "{标题}",
      "status": "pending | active | done",
      "completedAt": null,
      "subTasks": [
        {
          "id": "M1-1",
          "title": "{任务}",
          "status": "pending | active | blocked | done",
          "completedAt": null
        }
      ]
    }
  ],
  "changeLog": []
}
```

---

## 三、版本不匹配处理

### 判断方法

读取文件的版本字段，与下表对比：

| 文件 | 当前版本 | 契约束份 |
|------|---------|---------|
| `docs/PLAN.md` | `version` | 1.0 |
| `.target-trigger` | `version` | 1.0 |
| `.task-split.json` | `version` | 1.0 |
| `.target-state.json` | `schemaVersion` | 1.0 |

### 处理规则

```
版本匹配 → 正常读取
版本不匹配 → 提示用户，不卡住
```

### 提示模板

```markdown
## ⚠️ 版本不匹配

**文件**：`{文件名}`
**当前版本**：`{版本号}`
**契约束份版本**：`1.0`

**说明**：文件格式可能与当前 Skill 不兼容，可能出现解析问题。

**建议**：
1. 确认文件内容是否正确
2. 如有问题，请重新生成该文件

是否继续？
```

---

## 四、变更记录

| 日期 | 文件 | 变更内容 | 影响范围 |
|------|------|---------|---------|
| 2026-05-17 | 所有文件 | 初始版本 | — |

---

## 五、更新规则

当某个 Skill 更新了输出格式时：

1. 在本文件中更新对应文件的格式定义
2. 更新「变更记录」表格
3. 在 gql-skills 的变更记录中添加说明
4. 通知相关 Skill 的维护者
