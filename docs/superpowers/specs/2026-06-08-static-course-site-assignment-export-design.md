# 静态课程网站与本地作业导出设计

## 背景

当前项目是一套 Agent 学习课程，课程主体以 Markdown 文件维护，包括阶段路线图、六个阶段课程、参考项目和补充说明。现有内容适合编写和版本管理，但阅读体验、课后作业填写、作业格式统一和课程内容更新同步还缺少专门设计。

本设计目标是在不引入服务端、数据库、登录系统的前提下，把现有 Markdown 课程转化为静态学习网页，并支持学习者在浏览器中填写作业、保存本地草稿、导出标准 Markdown 作业文件。

## 目标

1. 保留 Markdown 作为课程内容的唯一可信源。
2. 提供更适合学习的静态网页阅读体验。
3. 用结构化作业模板替代自由散落的课后题文本。
4. 支持浏览器本地草稿保存。
5. 支持将作业导出为标准 Markdown 文件。
6. 支持课程 Markdown 的新增、更新、删除后的构建期同步。

## 非目标

1. 不做服务端提交。
2. 不做用户登录。
3. 不做数据库存储。
4. 不做在线批改和老师点评。
5. 不做多人协作。
6. 不做复杂课程版本迁移，只做版本提示。

## 信息架构

建议逐步调整为以下目录结构：

```text
content/
  courses/
    course-01-basic-cognition.md
    course-02-technical-foundation.md
    course-03-architecture.md
    course-04-productization.md
    course-05-frontier.md
    course-06-portfolio.md

  assignments/
    course-01/
      product-analysis.schema.json
      concept-note.schema.json
      paradigm-classification.schema.json
    course-02/
      react-agent.schema.json
      rag-design.schema.json
      prompt-iteration.schema.json
      evaluation-set.schema.json
    course-03/
      harness-refactor.schema.json
      orchestration-comparison.schema.json
      memory-system.schema.json
      evaluation-framework.schema.json
      guardrails.schema.json
      tracing.schema.json
    course-04/
      interaction-upgrade.schema.json
      reliability-hardening.schema.json
      cost-analysis.schema.json
      failure-review.schema.json
    course-05/
      mcp-practice.schema.json
      ecosystem-scan.schema.json
      frontier-exploration.schema.json
    course-06/
      knowledge-assistant.schema.json
      code-review-agent.schema.json
      domain-agent-product.schema.json

public/generated/
  course-index.json
  assignment-index.json
```

第一版可以不立刻移动现有课程文件。解析脚本可以先扫描项目根目录的 `course-*.md`，等静态站稳定后再迁移到 `content/courses/`。

## 课程 Markdown 规范

每个课程 Markdown 顶部增加 frontmatter：

```yaml
---
id: course-01
title: 阶段一：基础认知
order: 1
version: 1.0.0
updatedAt: 2026-06-08
status: published
---
```

字段含义：

```text
id: 稳定课程 ID，不随文件名变化
title: 课程展示标题
order: 课程排序
version: 课程版本
updatedAt: 内容更新时间
status: published / draft / archived
```

课程新增、删除、改名、重排都应通过 frontmatter 和构建期索引处理，不应让网页代码硬编码课程文件路径。

## 构建期同步

构建脚本负责扫描课程和作业模板，生成静态网页所需的数据。

```text
课程 Markdown
  -> 解析 frontmatter
  -> 提取标题层级
  -> 提取学习目标、前置输入、练习任务、交付物、验收标准
  -> 生成 course-index.json

作业 schema
  -> 校验 courseId 和 assignmentId
  -> 关联课程版本
  -> 生成 assignment-index.json
```

支持的同步行为：

```text
新增课程: 新增 Markdown + frontmatter，重新构建后出现在课程列表
删除课程: 删除 Markdown 或 status=archived，重新构建后隐藏
更新课程: 修改 Markdown version/updatedAt，重新构建后展示新版本
新增作业: 新增 schema，重新构建后出现作业入口
删除作业: 删除 schema 或标记 archived，重新构建后隐藏
```

## 页面设计

静态站第一版包含四类页面：

```text
/
  课程总览

/courses
  全部课程列表

/courses/:courseId
  课程阅读页

/assignments/:courseId/:assignmentId
  作业填写页
```

课程阅读页布局：

```text
左侧: 课程目录
中间: Markdown 正文
右侧: 学习目标、练习任务、交付物、验收标准
底部: 本课程作业入口
```

作业填写页布局：

```text
顶部: 课程、作业标题、课程版本
中间: schema 驱动的表单
右侧: 提交要求、验收标准、导出状态
底部: 保存草稿、清空草稿、导出 Markdown
```

## 作业 Schema

作业模板用轻量 schema 描述，不依赖服务端。

示例：

```json
{
  "id": "product-analysis",
  "courseId": "course-01",
  "title": "Agent 产品体验总结",
  "description": "任选 3 款 Agent 产品，完成体验拆解报告。",
  "outputFilename": "course-01-product-analysis.md",
  "fields": [
    {
      "id": "student_name",
      "label": "姓名",
      "type": "text",
      "required": true
    },
    {
      "id": "product_name",
      "label": "产品名称",
      "type": "text",
      "required": true
    },
    {
      "id": "scenario",
      "label": "使用场景",
      "type": "textarea",
      "required": true
    },
    {
      "id": "agentic_behavior",
      "label": "观察到的 Agent 行为",
      "type": "textarea",
      "required": true
    },
    {
      "id": "strengths",
      "label": "优点",
      "type": "textarea"
    },
    {
      "id": "limitations",
      "label": "问题与限制",
      "type": "textarea"
    },
    {
      "id": "conclusion",
      "label": "总结判断",
      "type": "textarea",
      "required": true
    }
  ]
}
```

第一版字段类型控制在少量稳定组件：

```text
text
textarea
select
multi-select
number
url
date
checkbox
repeater
```

`repeater` 用于产品拆解、失败案例、评测任务等重复条目。

## 作业类型

全课程作业抽象为六类：

```text
产品分析类: 产品名、场景、观察维度、优点、限制、设计取舍、总结
技术实现类: 仓库链接、运行方式、核心代码、截图说明、测试结果、问题记录
实验对比类: 实验目标、方案 A、方案 B、指标、数据、结论
架构设计类: 背景、架构图、模块说明、数据流、权衡、风险
评测报告类: 评测集、指标、运行结果、失败分类、改进计划
复盘总结类: 目标、实际结果、失败案例、原因分析、下一步
```

各课程通过 schema 选择和组合这些字段，不需要为每个作业手写页面。

## 本地草稿

浏览器使用 `localStorage` 保存草稿。key 包含课程、作业和课程版本：

```text
assignment-draft:course-01:product-analysis:v1.0.0
```

如果课程版本更新，页面提示：

```text
当前草稿基于课程 v1.0.0，课程已更新到 v1.1.0，请确认是否继续使用旧草稿。
```

第一版只提示版本差异，不自动迁移草稿字段。

## Markdown 导出

导出的作业文件必须包含元信息，确保离线文件仍可追踪来源。

```markdown
---
courseId: course-01
courseTitle: 阶段一：基础认知
assignmentId: product-analysis
assignmentTitle: Agent 产品体验总结
courseVersion: 1.0.0
submittedAt: 2026-06-08
---

# Agent 产品体验总结

## 基本信息

- 姓名：张三
- 产品名称：Claude Code

## 使用场景

...

## 观察到的 Agent 行为

...

## 优点

...

## 问题与限制

...

## 总结判断

...
```

导出文件命名建议：

```text
course-01-product-analysis-2026-06-08.md
```

学习者可以自行保存，或放入仓库约定目录：

```text
submissions/
  course-01/
    course-01-product-analysis-2026-06-08.md
```

## 版本与历史提交

作业导出文件通过以下字段绑定课程上下文：

```text
courseId
assignmentId
courseVersion
```

不要将作业绑定到课程文件路径。课程文件改名、移动目录、标题更新都不应该影响历史作业的可追踪性。

## 第一版范围

第一版实现：

```text
1. 静态课程总览页
2. 课程阅读页
3. 作业列表和作业入口
4. schema 驱动的作业表单
5. 本地草稿保存
6. Markdown 导出
7. 构建期课程和作业索引生成
```

暂不实现：

```text
1. 登录
2. 在线提交
3. 老师批改
4. 数据库
5. 权限系统
6. 多人协作
7. 复杂版本迁移
```

## 验证标准

1. 新增一个课程 Markdown 后，重新构建即可在课程列表看到它。
2. 修改课程版本后，阅读页显示新版本。
3. 删除或归档课程后，课程列表不再展示它。
4. 新增一个作业 schema 后，课程页出现对应作业入口。
5. 作业表单刷新页面后能恢复草稿。
6. 导出的 Markdown 包含课程、作业、版本和填写内容。
7. 导出的 Markdown 可以独立阅读，不依赖网页上下文。

## 后续实施建议

先实现最小闭环：扫描现有 `course-*.md`、渲染课程列表和阅读页、手写一到两个作业 schema、完成本地草稿和 Markdown 导出。等闭环稳定后，再补齐全部课程的作业 schema，并考虑是否迁移目录结构。
