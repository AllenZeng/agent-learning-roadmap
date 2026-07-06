#!/usr/bin/env python3
"""
课程五 05-03 Memory 示例 —— 交互式 Memory 生命周期演示

模拟知识助手从周一到周三的跨会话对话，展示 Memory 系统的完整生命周期：
  识别候选记忆 → 写入决策 → 存储 → 召回 → 更新与遗忘

纯 Python 标准库实现（bag-of-words 向量），无需外部依赖。

用法：
  python3 memory_demo.py           # 交互模式（每一步按 Enter 继续）
  python3 memory_demo.py --auto    # 自动模式（适合查看完整输出）
"""

import json
import os
import hashlib
import re
import shutil
import sys
import time
from datetime import datetime, timedelta

# ============================================================
# Lightweight Memory implementation (core logic, about 200 lines)
# ============================================================

class AgentMemory:
    """分层存储 + 写入守卫 + 语义召回 + 审计日志"""

    def __init__(self, storage_dir="./memory_store"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.pref_path = os.path.join(storage_dir, "preferences.json")
        self.facts_path = os.path.join(storage_dir, "facts.json")
        self.history_path = os.path.join(storage_dir, "task_history.json")
        self.audit_path = os.path.join(storage_dir, "audit.jsonl")
        self.preferences = self._load(self.pref_path, {})
        self.facts = self._load(self.facts_path, [])
        self.history = self._load(self.history_path, [])
        self.session = {}
        self.pending = []

    def _load(self, path, default):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _audit(self, action, detail):
        entry = {"ts": datetime.now().isoformat(), "action": action, **detail}
        with open(self.audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # ── Identify candidate memories ──
    def identify_candidates(self, user_message):
        candidates = []
        for pat in [r"以后[^，。]*", r"每次[^，。]*", r"不要[^，。]*", r"默认[^，。]*"]:
            for m in re.findall(pat, user_message):
                candidates.append({"type": "preference", "content": m,
                    "source": "user_explicit", "confidence": 0.95, "sensitive": False})
        # Sensitive-information detection
        if re.search(r"(?:api[_\s]?key|secret|token|密码)\s*[：:=]\s*\S+", user_message, re.I):
            candidates.append({"type": "sensitive", "content": "[敏感信息]",
                "source": "detected", "confidence": 0.99, "sensitive": True})
        # Temporary constraint
        for m in re.findall(r"这次[^，。]*", user_message):
            candidates.append({"type": "temporary", "content": m,
                "source": "user_explicit", "confidence": 0.9, "sensitive": False})
        return candidates

    # ── Write guard ──
    def should_remember(self, c):
        if c.get("sensitive"): return False, "sensitive"
        if c.get("type") == "temporary": return False, "temporary"
        if c.get("confidence", 0) < 0.5: return False, "low_confidence"
        # Conflict detection
        if c["type"] == "preference":
            for k, v in self.preferences.items():
                if v.get("category") == c.get("category") and v.get("content") != c.get("content"):
                    return True, f"conflict: replacing old preference"
        return True, "ok"

    # ── Write ──
    def write(self, entry):
        ok, reason = self.should_remember(entry)
        if not ok:
            self._audit("write_rejected", {"reason": reason})
            return {"status": "rejected", "reason": reason}
        mid = "mem_" + hashlib.md5(entry.get("content", "").encode()).hexdigest()[:10]
        record = {"id": mid, **entry, "created_at": datetime.now().isoformat(),
                  "updated_at": datetime.now().isoformat(), "access_count": 0}
        if entry["type"] == "preference":
            key = (entry.get("category", "general") + "_" +
                   hashlib.md5(entry.get("content", "").encode()).hexdigest()[:6])
            old = self.preferences.get(key)
            # If no match is found by key, search conflicts by category (different content but same category)
            if not old:
                for k, v in self.preferences.items():
                    if v.get("category") == entry.get("category") and v.get("content") != entry.get("content"):
                        old = v
                        break
            if old and old.get("content") != entry.get("content"):
                record["supersedes"] = old["id"]
                record["version"] = old.get("version", 1) + 1
                old["status"] = "superseded"
                old["superseded_by"] = mid
                old["updated_at"] = datetime.now().isoformat()
            self.preferences[key] = record
            self._save(self.pref_path, self.preferences)
        elif entry["type"] == "fact":
            self.facts.append(record)
            self._save(self.facts_path, self.facts)
        elif entry["type"] == "task_result":
            self.history.append(record)
            self.history = self.history[-500:]
            self._save(self.history_path, self.history)
        self._audit("write_accepted", {"id": mid, "type": entry["type"]})
        return {"status": "written", "id": mid}

    # ── Recall ──
    def recall(self, task, limit=5):
        relevant = []
        # Keyword matching (supports mixed Chinese/English: character bigrams for Chinese, whitespace tokens for English)
        task_grams = self._tokenize(task)
        for k, pref in self.preferences.items():
            if pref.get("status") == "superseded": continue
            mem_grams = self._tokenize(pref.get("content", ""))
            overlap = len(task_grams & mem_grams)
            if overlap >= 1:  # Preference matching uses a low threshold (at least one token/bigram overlap)
                relevant.append({**pref, "score": min(0.95, 0.7 + overlap * 0.05), "match": "keyword"})
        # Semantic recall (bag-of-words vectors)
        tv = self._embed(task)
        for fact in self.facts:
            if fact.get("status") == "superseded": continue
            fv = self._embed(fact.get("content", ""))
            score = self._cosine(tv, fv)
            if score > 0.3: relevant.append({**fact, "score": round(score, 3), "match": "semantic"})
        # Sort by score x time decay
        for m in relevant:
            days = self._days_since(m.get("updated_at", m.get("created_at")))
            tf = max(0.5, 1.0 - days / 180)
            m["final"] = round(m["score"] * tf + min(0.1, m.get("access_count", 0) * 0.01), 3)
        relevant.sort(key=lambda x: x["final"], reverse=True)
        result = relevant[:limit]
        for m in result:
            m["access_count"] = m.get("access_count", 0) + 1
        return result

    def _tokenize(self, text):
        """中英文混合分词：中文用字符 bigram，英文/数字用空格分词"""
        text = text.lower()
        tokens = set()
        # Extract English/numeric words
        for w in re.findall(r'[a-z0-9]+', text):
            tokens.add(w)
        # Extract Chinese character bigrams
        chinese = re.findall(r'[一-鿿]+', text)
        for seg in chinese:
            for i in range(len(seg) - 1):
                tokens.add(seg[i:i+2])
        return tokens

    def _embed(self, text):
        vec = [0.0] * 128
        for i in range(len(text) - 2):
            idx = hash(text[i:i+3].lower()) % 128
            vec[idx] += 1.0
        norm = (sum(v * v for v in vec)) ** 0.5
        return [v / norm for v in vec] if norm > 0 else vec

    def _cosine(self, a, b):
        return max(0.0, sum(x * y for x, y in zip(a, b)))

    def _days_since(self, ts):
        if not ts: return 999
        return (datetime.now() - datetime.fromisoformat(ts)).total_seconds() / 86400

    # ── Update / delete / decay ──
    def update(self, mid, updates):
        for store, path in [(self.preferences, self.pref_path), (self.facts, self.facts_path), (self.history, self.history_path)]:
            items = store.values() if isinstance(store, dict) else store
            for m in (items if isinstance(items, list) else list(items)):
                if m.get("id") == mid:
                    m.update(updates)
                    m["updated_at"] = datetime.now().isoformat()
                    self._save(path, store)
                    return {"status": "updated"}
        return {"status": "not_found"}

    def delete(self, mid):
        for store, path in [(self.preferences, self.pref_path), (self.facts, self.facts_path), (self.history, self.history_path)]:
            if isinstance(store, dict):
                for k in [k for k, v in store.items() if v.get("id") == mid]:
                    del store[k]
                    self._save(path, store)
                    return {"status": "deleted"}
            else:
                before = len(store)
                store[:] = [m for m in store if m.get("id") != mid]
                if len(store) < before:
                    self._save(path, store)
                    return {"status": "deleted"}
        return {"status": "not_found"}

    def decay(self):
        stats = {"expired": 0, "stale": 0}
        for k, pref in self.preferences.items():
            if pref.get("last_accessed_at"):
                days = (datetime.now() - datetime.fromisoformat(pref["last_accessed_at"])).days
                if days > 90: pref["status"] = "stale"; stats["stale"] += 1
        self._save(self.pref_path, self.preferences)
        return stats

    def list_all(self):
        all_mem = list(self.preferences.values()) + self.facts + self.history
        all_mem.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return all_mem

    def start_session(self, uid="user-001"):
        self.session = {"uid": uid, "started": datetime.now().isoformat(), "turns": 0}
        self.decay()
        self._audit("session_start", {"uid": uid})

    def end_session(self):
        self._audit("session_end", {"turns": self.session.get("turns", 0)})
        self.session = {}


# ============================================================
# Interactive demo
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RED = "\033[31m"

def wait(msg, auto=False):
    """非交互模式下自动继续，交互模式下等待用户按 Enter"""
    if auto:
        print(f"\n{DIM}── 自动进入下一步 ──{RESET}")
        time.sleep(0.5)
    else:
        input(msg)

def show_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════╗
║     课程五 05-03 Memory 生命周期演示                         ║
║     模拟知识助手 周一 → 周三 的跨会话 Memory 行为              ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def show_memory_state(memory, label=""):
    """可视化当前 Memory 存储状态"""
    print(f"\n{YELLOW}{BOLD}📦 {label}{RESET}")
    prefs = memory.preferences
    if prefs:
        print(f"  {BOLD}preferences:{RESET}")
        for k, v in prefs.items():
            status = f"{RED}stale{RESET}" if v.get("status") == "stale" else f"{DIM}superseded{RESET}" if v.get("status") == "superseded" else f"{GREEN}active{RESET}"
            print(f"    [{v['id']}] {v.get('content','')[:60]} ({status})")
    facts = [f for f in memory.facts if f.get("status") != "superseded"]
    if facts:
        print(f"  {BOLD}facts:{RESET}")
        for f in facts:
            print(f"    [{f['id']}] {f.get('content','')[:60]}")
    hist = memory.history[-3:]
    if hist:
        print(f"  {BOLD}task_history (recent 3):{RESET}")
        for h in hist:
            print(f"    [{h['id']}] {h.get('content','')[:60]}")

def show_recall_results(recalled):
    """展示召回结果"""
    if not recalled:
        print(f"  {DIM}(无相关记忆){RESET}")
        return
    for i, r in enumerate(recalled):
        match_icon = "🔑" if r.get("match") == "keyword" else "🔍"
        print(f"  {match_icon} #{i+1} (score: {r.get('final', r.get('score', 0))})  {r.get('content','')[:80]}")

def simulate(auto=False):
    show_banner()

    # Clean up old data
    if os.path.exists("./memory_store"):
        shutil.rmtree("./memory_store")

    memory = AgentMemory("./memory_store")

    # ═══════════════════════════════════════════════════
    # SESSION 1: Monday
    # ═══════════════════════════════════════════════════
    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  SESSION 1：周一 10:00-10:45{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")
    print(f"\n{DIM}[会话开始] decay check: 无过期记忆（系统初始化）{RESET}")

    # User input 1
    msg = "以后写技术文章，先给我大纲确认，再展开正文。语气直接，不要营销化。"
    print(f"\n{GREEN}👤 用户：{msg}{RESET}")

    candidates = memory.identify_candidates(msg)
    print(f"{DIM}[identify] 识别到 {len(candidates)} 条候选记忆{RESET}")
    for c in candidates:
        # Use a finer-grained category to prevent preferences of the same broad type from overwriting each other
        cat = "writing_workflow" if "大纲" in c["content"] or "先给" in c["content"] else \
              "writing_tone" if "语气" in c["content"] or "营销" in c["content"] else "writing_style"
        result = memory.write({**c, "category": cat})
        status = f"{GREEN}✅ 写入{RESET}" if result["status"] == "written" else f"{RED}❌ 拒绝: {result['reason']}{RESET}"
        print(f"  → {c['content'][:50]}... {status}")

    # User input 2
    msg2 = "我最近在用 TypeScript 写 Agent 框架，帮我看看这段代码"
    print(f"\n{GREEN}👤 用户：{msg2}{RESET}")
    print(f"{DIM}[identify] 此消息未触发显式偏好规则，但系统从行为中推断：用户可能偏好 TypeScript{RESET}")

    # Manually write an inferred preference (simulates a preference inferred by the system but not automatically captured by identify)
    result = memory.write({
        "type": "preference", "category": "code_style",
        "content": "用户可能偏好 TypeScript 示例代码",
        "source": "inferred", "confidence": 0.5, "sensitive": False,
    })
    status = f"{YELLOW}⚠️ 写入为候选记忆（低置信度推断，待用户确认）{RESET}" if result["status"] == "written" else f"{RED}❌ 拒绝{RESET}"
    if result["status"] == "written":
        # Mark as candidate
        memory.pending.append({"id": result["id"], "content": "用户可能偏好 TypeScript 示例代码"})
    print(f"  → 推断偏好: TypeScript 示例代码... {status}")

    # User input 3
    msg3 = "帮我写一篇 Agent Memory 的技术文章"
    print(f"\n{GREEN}👤 用户：{msg3}{RESET}")
    recalled = memory.recall(msg3, limit=5)
    print(f"{DIM}[recall] 召回 {len(recalled)} 条相关记忆:{RESET}")
    show_recall_results(recalled)
    print(f"\n{CYAN}🤖 Agent：（因为有 #1 偏好记忆，先输出大纲等待确认）{RESET}")

    # Write experience after the task is complete
    memory.write({"type": "task_result", "content": "先大纲再正文在技术文章中效果好，3轮迭代完成",
                  "source": "auto", "confidence": 0.8})
    print(f"{DIM}[write] 任务经验已记录{RESET}")

    show_memory_state(memory, "Session 1 结束时的 Memory 状态")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # SESSION 2: Tuesday (Cross-session!)
    # ═══════════════════════════════════════════════════
    wait(f"\n{DIM}按 Enter 进入 Session 2（周二，跨会话）...{RESET}", auto)

    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  SESSION 2：周二 09:00-09:30  ← 跨会话！{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")
    print(f"{DIM}[会话开始] decay check: 无过期（才过了一天）{RESET}")

    msg4 = "帮我写一篇 RAG 最佳实践的技术文章"
    print(f"\n{GREEN}👤 用户：{msg4}{RESET}")
    recalled2 = memory.recall(msg4, limit=5)
    print(f"{DIM}[recall] 跨会话召回 {len(recalled2)} 条相关记忆:{RESET}")
    show_recall_results(recalled2)
    if any("写作" in r.get("content", "") or "大纲" in r.get("content", "") for r in recalled2):
        print(f"\n{CYAN}🤖 Agent：（Memory 跨会话生效！先输出大纲，语气直接）{RESET}")
        print(f"    用户不需要重新说『先给大纲』——偏好跨会话保持了。{RESET}")

    memory.write({"type": "task_result", "content": "RAG 文章用先大纲方式完成，用户满意",
                  "source": "auto", "confidence": 0.8})

    show_memory_state(memory, "Session 2 结束时的 Memory 状态")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # SESSION 3: Wednesday (Preference changed!)
    # ═══════════════════════════════════════════════════
    wait(f"\n{DIM}按 Enter 进入 Session 3（周三，偏好变更）...{RESET}", auto)

    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  SESSION 3：周三 14:00-14:30  ← 偏好变更！{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")

    msg5 = "以后示例代码改用 Python"
    print(f"\n{GREEN}👤 用户：{msg5}{RESET}")
    candidates5 = memory.identify_candidates(msg5)
    for c in candidates5:
        c["category"] = "code_style"
        result = memory.write(c)
        if result["status"] == "written":
            print(f"  → {c['content'][:50]}... {GREEN}✅ 写入（检测到冲突，旧 TS 偏好已标记 superseded）{RESET}")
        else:
            print(f"  → {c['content'][:50]}... {RED}❌ 拒绝: {result['reason']}{RESET}")

    msg6 = "帮我写一篇 Python Agent 框架的技术文章"
    print(f"\n{GREEN}👤 用户：{msg6}{RESET}")
    recalled3 = memory.recall(msg6, limit=5)
    print(f"{DIM}[recall] 召回 {len(recalled3)} 条相关记忆:{RESET}")
    show_recall_results(recalled3)
    print(f"\n{CYAN}🤖 Agent：（用 Python 示例，不是 TS！偏好变更生效了）{RESET}")

    show_memory_state(memory, "Session 3 结束时的 Memory 状态")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  📊 完整生命周期总结{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    print(f"""
  ✅ 跨会话延续：Session 2 不需要重新说"先给大纲"
  ✅ 冲突替换：Session 3"用 Python"覆盖了"用 TS"
  ✅ 审计可见：旧 TS 偏好仍保留（superseded），可追溯
  ✅ 推断 vs 确认：推断偏好（TS）自动被显式声明（Python）覆盖
  ✅ 审计日志：{GREEN}memory_store/audit.jsonl{RESET} 记录了所有操作

  {DIM}查看存储文件：{RESET}
    {CYAN}memory_store/preferences.json{RESET}  - 用户偏好
    {CYAN}memory_store/facts.json{RESET}        - 长期事实
    {CYAN}memory_store/task_history.json{RESET} - 任务经验
    {CYAN}memory_store/audit.jsonl{RESET}       - 审计日志
""")


if __name__ == "__main__":
    auto_mode = "--auto" in sys.argv
    simulate(auto=auto_mode)
