# Chapter 7: Human-in-the-loop - When Agent should not decide for himself

[Return Course Five Document](./course-05-01-scenario-enhancement.md) | [Previous Chapter](./course-05-06-reflection.md) | [Next chapter](./course-05-08-multi-agent.md)

## Table of contents of this chapter

- [7.1 "It made my decision, and I wasn't there."](#71-it-made-my-decision-and-i-wasnt-there)
- [7.2 "Can do" is not the same as "should do" -- the gap between abilities and competencies.](#72-can-do-is-not-the-same-as-should-do----the-gap-between-abilities-and-competencies)
- [7.3 Five modes of HITL](#73-five-modes-of-hitl)
  - [7.3.1 Confirmation](#731-confirmation)
  - [7.3.2 Clarification model](#732-clarification-model)
  - [7.3.3 Takeover model (Takeover)](#733-takeover-model-takeover)
  - [7.3.4 Audit model (review)](#734-audit-model-review)
  - [7.3.5 Teaching feedback model (Teaching Feedback)](#735-teaching-feedback-model-teaching-feedback)
  - [7.3.6 Five model comparisons](#736-five-model-comparisons)
- [7.4 Design decision-making: what to ask, how often and how to present](#74-design-decision-making-what-to-ask-how-often-and-how-to-present)
  - [7.4.1 Risk classification: which operations require human intervention](#741-risk-classification-which-operations-require-human-intervention)
  - [7.4.2 Frequency control: Don't be too upset or too comfortable](#742-frequency-control-dont-be-too-upset-or-too-comfortable)
  - [7.4.3 Context: To enable humans to make quick judgements](#743-context-to-enable-humans-to-make-quick-judgements)
- [7.5 Learning from feedback](#75-learning-from-feedback)
- [7.6 Evolution course: from "all confirmed" to "precision intervention."](#76-evolution-course-from-all-confirmed-to-precision-intervention)
- [7.7 HITL 's five reverse modes](#77-hitl-s-five-reverse-modes)
- [7.8 When don't need HITL](#78-when-dont-need-hitl)
- Summary of this chapter
- [Runable Example](#runable-example)

---

## 7.1 "It made my decision, and I wasn't there."

Agent, a knowledge assistant, has access to RAG, Memory, Context Engineering, Planning and Reflection. It retrieves your notes, remembers your preferences, manages context, dismantles tasks, fixes failure. You start to trust it.

Then one day, you let it sort out the papers.

```text
你："帮我把 /tmp/logs 下超过 30 天的日志文件清理一下。"
Agent："好的。" → 调用 delete_file → 开始删除
```

You suddenly saw a file name flashing...`.env.backup`I don't know. That's the backup file you manually put in last week, not the log. You didn't have time to stop. The papers are gone.

It's not Agent "gets bad." It's done according to your instructions. The problem is: **The task of cleaning up log files has some consequences you didn't say (env backup cannot be deleted), and Agent is not aware of these implied constraints.** Another scenario: you're testing a guest suit, Agent. The user said, "I want a refund."

```text
用户："这个产品不好用，我要退款。"
Agent："非常抱歉给您带来了不好的体验。我已为您提交了全额退款申请，款项将在 3-5 个工作日内退回。"
```

You stare at the screen, your hands sweat. Refund strategies have not yet been defined — maximum amounts, conditions for refunds, approval process. Agent made a decision for you.

These scenarios point to the same problem: **Agent has the capacity to carry out an operation, but this does not mean it should be autonomous.** There is a gap between capacities and competencies — not a technology divide, but a judgement divide. The model doesn't know your business rules, your risk preferences, the implicit constraints you don't know.

That's the problem for Human-in-the-loop (HITL): **In Agent's decision-making chain, insert human judgment in the right place.**

## 7.2 "Can do" is not the same as "should do" -- the gap between abilities and competencies.

We need to clear up the meaning of several concepts in the HITL context:

```text
能力（Capability）：Agent 在技术上能执行什么操作。
  例：Agent 可以调用 delete_file、可以调用 refund_api、可以发送邮件。

权限（Permission）：系统允许 Agent 自主执行什么操作。
  例：delete_file 被允许，但需要人类确认。refund_api 完全禁止自主调用。

判断（Judgment）：这个具体操作在当下是否合适。
  例：删除 /tmp/logs/access_2026.log 是合适的。删除 /tmp/logs/.env.backup 不是。
```

The essence of HITL is that **when Agent's ability covers an operation, but the system cannot afford to return judgment to humans when all the rules of judgement are exhausted at the code level.** Why not write the rules in the code? Because:

- `.env.backup`Is that a log file? Not by naming rules, but it is under /tmp/logs directory. Agent didn't judge it.
- Is the full refund appropriate? Depending on your refund policy, user history, value of orders... it's not a few lines if-else can cover.

The HITL is not an adequate security mechanism and cannot be a substitute for permission verification, input filtering, tool isolation, audit logs and Guardrails. It is more like an enhanced decision-making mechanism in the line of defence**— the introduction of human judgement as an enhancement when Agent's autonomous judgement does not cover the risks.

## 7.3 Five modes of HITL

HITL is not a simple "play a confirmation box". Depending on the timing and depth of human intervention, there are five models.

### 7.3.1 Confirmation **When to use**: Agent has decided what to do, but the operation is risky and requires human nodding.

```text
Agent："我将删除以下 12 个文件：
  - /tmp/logs/access_20260501.log (32MB, 45 天前)
  - /tmp/logs/error_20260515.log (8MB, 31 天前)
  - ……
  [确认执行] [取消] [修改范围]"
```

Identification of the three design elements of the model: **1. Presentation of "effects" instead of "operations"**```text
❌ 差："确认调用 delete_file？"
   人类不知道要删什么、删多少、有什么影响。

✅ 好："将删除 12 个文件，共 156MB。这些文件上次修改超过 30 天。
   注意：/tmp/logs 目录下还有 3 个非日志文件（.env.backup, config.json, README），
   它们不会被删除。"
```
**2. Provide intermediate options, more than "Yes/No"**```text
[确认全部] [只删 .log 文件] [让我逐个确认] [取消]
```

The second option is to give humans a preference for confirmation. The granting of intermediate options has improved the quality of decision-making. **3. Complete but not lengthy context of confirmation** Humans need to see what they want to do, why they think they should do it, what risks they have, what they don't.

### 7.3.2 Clarification model **When to use**: Agent is uncertain about the user's intentions and needs human clarity.

```text
你："把最近的文章整理一下。"
Agent："'最近的文章'可能指：
  A. 最近 7 天写的文章（共 3 篇）
  B. 最近修改过的文章（共 8 篇）
  C. 最近打开过的文章（共 5 篇）
  你指的是哪种？"
```

Clarify the difference between mode and confirmation mode: Confirm "I have decided, you nod", clarify "I need you to help me decide."

Clarification of the design elements of the model:

- **Specific options are given, rather than an open question.** "Please specify your needs."
- **Each option is accompanied by a number or an example,** allowing humans to choose on the basis of information rather than speculation.
- **Provides an "other" option** so that humans can give the answers that Agent didn't consider.

### 7.3.3 Takeover model (Takeover) **When to use**: the operation is too complex or too sensitive, Agent should not do it himself, and control should be returned to mankind.

```text
Agent："检测到数据库迁移脚本涉及以下操作：
  - 修改 users 表的 email 字段类型
  - 删除 deprecated_records 表
  
  这类操作需要人工执行。我已准备好迁移脚本：
  /tmp/migration_20260629.sql
  
  执行后请回复'已完成'，我会继续后续步骤。"
```

Essential difference between takeover and confirmation: confirmation is Agent enforcement, human permit. Taking over is **human execution, Agent waiting**. Agent retreats to the auxiliary role -- it is prepared, it explains, it waits, but it does not operate.

Application of the takeover model:
- Database Schema Change
- Production environment deployment
- Operations involving compliance approval
- Any operation that does wrong can't just roll back.

### 7.3.4 Audit model (review) **When the output was completed with**: Agent, but required human examination of quality or selection in multiple programmes.

```text
Agent："技术方案已完成，共 4 个部分：
  1. 架构概述（已生成）
  2. API 设计（已生成）
  3. 数据库设计（已生成）
  4. 安全考虑（已生成，标注了 3 个待确认点）
  
  [查看全文] [逐节审核] [修改某节] [通过]"
```

The core of the audit model is to enable humans **to quickly position what needs attention**. Agent should take the initiative:
- It's not certain.
- There are many reasonable options.
- Where it advises, but needs human tablets.

Humans should not be allowed to read the full text in order to judge. **Stating uncertainty as the most valuable output of the audit model.**

### 7.3.5 Teaching feedback model (Teaching Feedback) **When did you use**: Agent did something wrong or not good enough, humans did it, Agent learned from it.

```text
Agent："我为你生成了发布 checklist。"
你："第 3 项漏了数据库备份步骤。第 6 项的检查命令不对，应该用 pytest 而不是 unittest。"
Agent："已修正。我注意到你在这个项目中一直使用 pytest。我将在 Memory 中更新：
  '项目 test_runner 偏好：pytest（非 unittest）'
  以后生成 checklist 时也会自动包含数据库备份步骤。"
```

Pedagogical feedback is the intersection of HITL and Memoory. Every human amendment should be captured as reusable knowledge. There are three levels:

| Level | What did you learn? | Scope of impact |
|---|---|---|
|**Immediate amendment** | This time it's right. | Current task only |
|**Preferences for updates** | Users like pytest | Follow-up to current projects |
|**Model study** | Release checklist must contain backup data. | Release type assignments for all projects |

Pedagogical feedback does not overzealate "self-learning". V0 is enough for immediate correction. The preference for renewal and model learning requires the collaboration of the Memoory system (see chapter III).

### 7.3.6 Five model comparisons

| Mode | Human role | Agent Role | Time for intervention | Typical scene |
|---|---|---|---|---|
|**Confirmed** | Licenser | Executor | Before execution | Delete Files, Send Mail, Git Push |
|**Clarification** | Definer | Executor | After understanding | Fuzzy demand, multi-dimensional command |
|**Took over** | Executor | Supporters | On implementation | Database migration, production deployment |
| Audit**| Reviewer | Creator | After output | Code review, programme review |
|**Teaching feedback** | Coach. | Learner | After error | Output does not match expectations, preference changes |

## 7.4 Design decision-making: what to ask, how often and how to present

### 7.4.1 Risk classification: which operations require human intervention

Not all operations need HITL. The classification is based on: **The irreversibility of the operation and the severity of the consequences.** | Risk level | Operational characteristics | HITL Mode | Example: |
|---|---|---|---|
|**Low** | Read-only, no side effects, repeatable | No need to intervene. | Read files, search codes, generate text |
| of the | Writing but rolling back with small impact | Confirmation (quantity available) | Create/edit files, send drafts |
|**High** | Writing and difficult to roll back, affecting external systems | Individual confirmation | Delete files, Git committee, API writing |
|**Key** | Unreversible, compliance/funding/security | Take over or confirm on a case-by-case basis + audit | Database migration, refunds, deployment, change of authority |

The hierarchy is not once and for all. The risk level of an operation changes with context:
- `delete_file`Remove the risk in the temporary file
- `delete_file`Delete`~/.ssh/`Key risks
- `send_email`Send drafts to colleagues
- `send_email`Group sent to 1,000 users

The risk classification should therefore not be based solely on the name of the tool, but on the parameters and context.

### 7.4.2 Frequency control: Don't be too upset or too comfortable

The hardest thing about HITL design is not "what to ask," but "how often." **Too often**: Human beings become "confirming robots". Each step points to confirmation that the user will soon develop a muscle memory — a "yes" without looking. HITL is nothing. **Too thin an effect**: Humans lose their sense of what Agent is doing. And when the problem was discovered, Agent had done ten irreversible operations.

Several strategies for frequency control: **Strategy I: batch confirmation**```text
❌ 单个确认：
  "确认删除 access_20260501.log？" [确认]
  "确认删除 error_20260515.log？" [确认]
  "确认删除 debug_20260520.log？" [确认]
  …（12 次）

✅ 批次确认：
  "将删除以下 12 个文件，共 156MB。其中 11 个为 .log 文件，1 个为 .txt 文件。
   [确认全部] [只删 .log 文件] [逐个确认] [取消]"
```
**Strategy II: Building trust**If the user confirms the same operation five times in a row, you can ask: "Do you trust me in the operation of the same file, and don't confirm it item by item?"**Strategy III: Summary retroactive confirmation**Not to confirm each step before implementation, but to provide a summary after implementation to allow users to confirm the overall direction:

```text
"上一阶段完成：已收集 8 篇相关文档，共 32KB。准备进入写作阶段。
 [继续] [查看文档列表] [调整方向]"
```
**Strategy IV: Decline of trust based on session**In the same session, Agent's judgment of user preferences will be more accurate. But after the break-up, trust should be reset — because mandates may be different.

### 7.4.3 Context: To enable humans to make quick judgements

When humans make HITL decisions, they also face a lack of information. You play a confirmation box: "Agent's gonna do a refund operation, confirm?" -- in that case, what do humans think?

OK. HITL design gives a simplified but complete decision-making context**when requesting human decision-making:

```text
Agent 请求执行退款操作：

▸ 用户：张三 (ID: 12847)
▸ 订单：ORD-20260629-0042
▸ 金额：¥299.00（全额）
▸ 原因：用户反馈"产品功能与描述不符"
▸ 用户历史：注册 2 年，此前 0 次退款申请
▸ 订单状态：已支付，未发货

Agent 判断：符合退款条件（7 天无理由，未发货）

[批准退款] [拒绝并说明原因] [转为人工处理]
```

Key design principles:

1.**Highlighted anomalies**: if "0 previous refund requests" becomes "5 previous refund requests", it should be highlighted in different colours/marks
2.**Agent's judgement is based on transparency**: not only what Agent wants to do, but also why.
3.**Provide context-related options**: not only yes/no, but also intermediate options such as "to manual processing"

## 7.5 Learning from feedback

HITL every intervention is marked once. Humans say "yes" or "no" and these signals are wasted if they are used only for current decision-making.

Three levels of learning:**Level 1: Immediate application (Always)**Human decisions affect the continuing direction of the current task. "No refunds" – Agent stopped the refund process and informed the user.**Level 2: Prefer Update (in collaboration with Memoory)**When humans repeatedly confirm or reject the same operation, it updates memory:

```text
"用户偏好更新：对 /tmp/logs 目录下的文件清理操作，用户已连续 3 次确认同类操作。
下次可以降低确认频率（批次确认即可）。"
```
**Level III: strategy adjustments (needs manual review)**Analyzing from HITL data: Which operations have too low pass rate (notation Agent)? Which operators are never rejected (may not need HITL)?

```text
HITL 数据分析（过去 30 天）：
- read_file 确认：120 次，通过率 100%  → 考虑移除确认
- delete_file 确认：45 次，通过率 89%  → 保持确认
- refund 确认：8 次，通过率 50%       → 确认不够，考虑改为接管模式
- send_email 确认：30 次，通过率 97%  → 可降低为中风险操作
```

This analysis should not be implemented automatically — human beings should review and decide whether to adjust their strategies. The value of HITL data is that**makes policy adjustments sound, rather than the system itself.

## 7.6 Evolution course: from "all confirmed" to "precision intervention."

| Phase | What did you do? | Apply scene |
|---|---|---|
|**V0: All hands**| All hard-coded high-risk operations are banned. After manual human execution, Agent continues. | Prototype, internal tools |
|**V1: Critical operation confirmation**| Unified bomb confirmation box for writing (Yes/No) | First version with users |
|**V2: Risk classification + batch confirmation**| Use different HITL modes by risk level, same operation supports batch confirmation | Users start to use frequently |
|**V3: Context Presentation + Learning**| Confirm box shows the context of decision-making; rejected preferences are written in Memoory | User trust-building period |
|**V4: Data-based strategy adjustments**| Adjust risk classification and HITL mode with HITL data | mature products, continuous optimization |

Most projects start with V1. V0 is too conservative (Agent can't do anything useful), V4 needs to have enough user volume and use data to make sense.

## 7.7 HITL 's five reverse modes**Counter-model I: confirmed every step**Click the confirmation box before all tools are called. Result: User clicked 15 times in 30 seconds, and didn't look. HITL is nothing.**Correct practice**: intervention is limited to high-risk and critical operations. A low-risk operation allows it to be implemented automatically.**Anti-model II: insufficient information on confirmation boxes**```text
"Agent 要执行 write_file，确认？"
```

Users do not know what to write, where to write, why, and what to do. This confirmation box does not give the user any basis for judgement. **Correct practice**: A path to document, summary of changes, basis of judgement for Agent. **Counter-model III: HiTL as a security mechanism** Use the HITL to prevent Prompt Intervention or ultra vires operations. "Someone confirmed that no input verification was required." **Correct practice**: HITL is a decision-making enhancement, not a complete security option. Security requires authority, verification, isolation, audit and Guardrails to work together. Humans also make mistakes -- the attacker can design the context in which humans tend to "confirm". **Counter-module IV: no timeout** Agent waits for humans to confirm that humans are going to meet. Agent's been waiting. **Correct practice**: set timeout. Overtime behaviour depends on operational risk - low-risk operations can continue automatically and high-risk operations should be terminated safely. **Anti-Model V: All users treated equally** New and senior users see the same frequency of confirmation. **Correct practice**: allows users to adjust the HITL level. The Developer Model can reduce the frequency of confirmation, the Security Model increases the frequency of confirmation. Let users themselves control the degree of autonomy they are willing to assume.

## 7.8 When don't need HITL

1. **Low risk Pure information type Agent**: Agent, which answers only questions, does not perform operations, does not have the risk of instrumentic side effects and usually does not need to add HITL before each response. If, however, the output affects high-risk decisions such as medical, legal, financial, security, compliance and so forth, there is still a need for manual audits or clear waivers.
2. **read-only operation**: if all Agent's tools are read-only (reading files, searching, searching), there are no side effects. The HITL value is almost zero.
3. **Reversible, low-impact personal operations**: Agent only for your own use and can roll back, without key, privacy, production system or external dispatch. The HITL can reduce the frequency, but it should not be tacitly released for "personal use".
4. **There is a good automated validation**: the frequency of HITL can be significantly reduced if the tool is implemented with automated tests, lint, type checks as safety nets. Automatic validation is more stable in detectable nature than human confirmation, but is not a substitute for business intent, compliance judgement and user impact assessment.

## Runable Example

After this chapter is completed, you can compare the local example of the running course 5 05-07 with the local example of Human-in-the-loop:

- [Course 5 05-07 Human-in-the-load example](../examples/course-05-07-human-in-the-loop/README.md)

The example generates three scenarios around file cleansing, refund processing and release documents, with two versions of Python and Node.js demonstrating five HITL modes of intervention: confirmation, clarification, taking over, auditing and teaching feedback. You'll see the same.`delete_file`How the operation was determined to be medium, high or critical because of different pathways, reversibility and scope of impact; and how Agent presented consequences, anomalies, grounds for judgement and intermediate options when requesting human judgement.

Example also generated`hitl_audit.jsonl`and`hitl_memory.json`First, HITL decision-making itself should be audited rather than confined to bullet windows; and second, human auditing and correction can be converted into reuseable memory, such as "publishing checklist must include back-up steps for databases." This corresponds to the risk classification and context of chapter 7.4 and to feedback learning of 7.5.

The example is teaching realization, not a complete production safety framework: risk assessment usage rules are achieved, refunds and database migrations do not call on external systems, only printing decision context, subsequent process branches and audit records; running requires manual choice of HITL decision-making, directly by Enter using default options to facilitate continuous observation of the full process. The real system still requires permission verification, tool segregation, input filtering, audit logs and Guardrails.

```bash
# Python 版本
cd examples/course-05-07-human-in-the-loop/python
python3 hitl_demo.py
python3 -m unittest test_hitl_demo.py

# Node.js 版本
cd examples/course-05-07-human-in-the-loop/nodejs
npm start
```
