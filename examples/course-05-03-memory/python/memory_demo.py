#!/usr/bin/env python3
"""
Course 05-03 Memory example - interactive Memory lifecycle demo

Simulates a knowledge assistant's cross-session conversations from Monday to Wednesday to show the full Memory lifecycle:
  identify candidate memories -> write decision -> storage -> recall -> update and forgetting

Implemented with only the Python standard library (bag-of-words vectors), with no external dependencies.

Usage:
  python3 memory_demo.py           # Interactive mode (press Enter at each step)
  python3 memory_demo.py --auto    # Automatic mode (useful for viewing the full output)
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
    """Layered storage + write guard + semantic recall + audit log"""

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
        for pat in [r"from now on[^，。]*", r"every time[^，。]*", r"do not[^，。]*", r"default[^，。]*"]:
            for m in re.findall(pat, user_message):
                candidates.append({"type": "preference", "content": m,
                    "source": "user_explicit", "confidence": 0.95, "sensitive": False})
        # Sensitive-information detection
        if re.search(r"(?:api[_\s]?key|secret|token|password)\s*[：:=]\s*\S+", user_message, re.I):
            candidates.append({"type": "sensitive", "content": "[sensitive information]",
                "source": "detected", "confidence": 0.99, "sensitive": True})
        # Temporary constraint
        for m in re.findall(r"this time[^，。]*", user_message):
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
        """Mixed Chinese/English tokenization: Chinese uses character bigrams, English/numbers use whitespace tokens"""
        text = text.lower()
        tokens = set()
        # Extract English/numeric words
        for w in re.findall(r'[a-z0-9]+', text):
            tokens.add(w)
        # Extract Chinese character bigrams
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
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
    """Continue automatically in non-interactive mode; wait for the user to press Enter in interactive mode"""
    if auto:
        print(f"\n{DIM}── automatically continue to the next step ──{RESET}")
        time.sleep(0.5)
    else:
        input(msg)

def show_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════╗
║     Course 05-03 Memory lifecycle demo                         ║
║     Simulate a knowledge assistant's cross-session Memory behavior from Monday to Wednesday              ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def show_memory_state(memory, label=""):
    """Visualize current Memory storage state"""
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
    """Show recall results"""
    if not recalled:
        print(f"  {DIM}(No relevant memories){RESET}")
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
    print(f"{BOLD}  SESSION 1：Monday 10:00-10:45{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")
    print(f"\n{DIM}[session start] decay check: No expired memories (system initialization){RESET}")

    # User input 1
    msg = "When writing technical articles in the future, give me an outline for confirmation before expanding the body. Keep the tone direct, not marketing-oriented."
    print(f"\n{GREEN}👤 user：{msg}{RESET}")

    candidates = memory.identify_candidates(msg)
    print(f"{DIM}[identify] Identified {len(candidates)} candidate memories{RESET}")
    for c in candidates:
        # Use a finer-grained category to prevent preferences of the same broad type from overwriting each other
        cat = "writing_workflow" if "outline" in c["content"] or "outline first" in c["content"] else \
              "writing_tone" if "tone" in c["content"] or "marketing" in c["content"] else "writing_style"
        result = memory.write({**c, "category": cat})
        status = f"{GREEN}✅ Write{RESET}" if result["status"] == "written" else f"{RED}❌ reject: {result['reason']}{RESET}"
        print(f"  → {c['content'][:50]}... {status}")

    # User input 2
    msg2 = "I am using TypeScript to write an Agent framework; help me review this code"
    print(f"\n{GREEN}👤 user：{msg2}{RESET}")
    print(f"{DIM}[identify] This message did not trigger an explicit preference rule, but the system inferred from behavior that the user may prefer TypeScript{RESET}")

    # Manually write an inferred preference (simulates a preference inferred by the system but not automatically captured by identify)
    result = memory.write({
        "type": "preference", "category": "code_style",
        "content": "User may prefer TypeScript example code",
        "source": "inferred", "confidence": 0.5, "sensitive": False,
    })
    status = f"{YELLOW}⚠️ Wrote as a candidate memory (low-confidence inference, awaiting user confirmation){RESET}" if result["status"] == "written" else f"{RED}❌ reject{RESET}"
    if result["status"] == "written":
        # Mark as candidate
        memory.pending.append({"id": result["id"], "content": "User may prefer TypeScript example code"})
    print(f"  → inferred preference: TypeScript example code... {status}")

    # User input 3
    msg3 = "Help me write a technical article about Agent Memory"
    print(f"\n{GREEN}👤 user：{msg3}{RESET}")
    recalled = memory.recall(msg3, limit=5)
    print(f"{DIM}[recall] Recall {len(recalled)} relevant memories:{RESET}")
    show_recall_results(recalled)
    print(f"\n{CYAN}🤖 Agent：（Because preference memory #1 exists, output an outline first and wait for confirmation){RESET}")

    # Write experience after the task is complete
    memory.write({"type": "task_result", "content": "Outline-first writing worked well for technical articles; completed in three iterations",
                  "source": "auto", "confidence": 0.8})
    print(f"{DIM}[write] Task experience recorded{RESET}")

    show_memory_state(memory, "Memory state at the end of Session 1")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # SESSION 2: Tuesday (Cross-session!)
    # ═══════════════════════════════════════════════════
    wait(f"\n{DIM}Press Enter to enter Session 2 (Tuesday, cross-session)...{RESET}", auto)

    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  SESSION 2：Tuesday 09:00-09:30  ← cross-session！{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")
    print(f"{DIM}[session start] decay check: No expiration (only one day has passed){RESET}")

    msg4 = "Help me write a technical article about RAG best practices"
    print(f"\n{GREEN}👤 user：{msg4}{RESET}")
    recalled2 = memory.recall(msg4, limit=5)
    print(f"{DIM}[recall] Cross-session recall {len(recalled2)} relevant memories:{RESET}")
    show_recall_results(recalled2)
    if any("writing" in r.get("content", "") or "outline" in r.get("content", "") for r in recalled2):
        print(f"\n{CYAN}🤖 Agent：（Memory Cross-session memory works! Output an outline first with a direct tone){RESET}")
        print(f"    The user does not need to repeat 'give the outline first'; the preference persisted across sessions.{RESET}")

    memory.write({"type": "task_result", "content": "RAG The article was completed outline-first and the user was satisfied",
                  "source": "auto", "confidence": 0.8})

    show_memory_state(memory, "Memory state at the end of Session 2")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # SESSION 3: Wednesday (Preference changed!)
    # ═══════════════════════════════════════════════════
    wait(f"\n{DIM}Press Enter to enter Session 3 (Wednesday, preference changed)...{RESET}", auto)

    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  SESSION 3：Wednesday 14:00-14:30  ← preference changed！{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    memory.start_session("user-001")

    msg5 = "Use Python for example code from now on"
    print(f"\n{GREEN}👤 user：{msg5}{RESET}")
    candidates5 = memory.identify_candidates(msg5)
    for c in candidates5:
        c["category"] = "code_style"
        result = memory.write(c)
        if result["status"] == "written":
            print(f"  → {c['content'][:50]}... {GREEN}✅ Wrote (conflict detected; the old TS preference was marked superseded){RESET}")
        else:
            print(f"  → {c['content'][:50]}... {RED}❌ reject: {result['reason']}{RESET}")

    msg6 = "Help me write a technical article about a Python Agent framework"
    print(f"\n{GREEN}👤 user：{msg6}{RESET}")
    recalled3 = memory.recall(msg6, limit=5)
    print(f"{DIM}[recall] Recall {len(recalled3)} relevant memories:{RESET}")
    show_recall_results(recalled3)
    print(f"\n{CYAN}🤖 Agent：（Use Python examples, not TS! The preference change took effect){RESET}")

    show_memory_state(memory, "Memory state at the end of Session 3")
    memory.end_session()

    # ═══════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  📊 Full lifecycle summary{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}")

    print(f"""
  ✅ Cross-session persistence: Session 2 did not require repeating "give the outline first"
  ✅ Conflict replacement: Session 3 "use Python" overrode "use TS"
  ✅ Auditable history: the old TS preference remains (superseded) and traceable
  ✅ Inference vs confirmation: inferred preference (TS) was automatically overridden by explicit declaration (Python)
  ✅ Audit log：{GREEN}memory_store/audit.jsonl{RESET} recorded all operations

  {DIM}View storage files：{RESET}
    {CYAN}memory_store/preferences.json{RESET}  - User preferences
    {CYAN}memory_store/facts.json{RESET}        - Long-term facts
    {CYAN}memory_store/task_history.json{RESET} - Task experience
    {CYAN}memory_store/audit.jsonl{RESET}       - Audit log
""")


if __name__ == "__main__":
    auto_mode = "--auto" in sys.argv
    simulate(auto=auto_mode)
