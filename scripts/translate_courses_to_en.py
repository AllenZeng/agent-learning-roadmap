#!/usr/bin/env python3
import hashlib
import json
import re
from pathlib import Path

from argostranslate import translate


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "courses"
TARGET_DIR = ROOT / "courses-en"
CACHE_PATH = ROOT / ".translation-cache-argos.json"

FILES = [
    "course-01-first-encounter.md",
    "course-02-evolution.md",
    "course-03-minimal-agent-loop.md",
    "course-04-tool-mechanism.md",
    "course-05-01-scenario-enhancement.md",
    "course-05-02-rag.md",
    "course-05-03-memory.md",
    "course-05-04-context-engineering.md",
    "course-05-05-planning.md",
    "course-05-06-reflection.md",
    "course-05-07-human-in-the-loop.md",
    "course-05-08-multi-agent.md",
    "course-05-09-composition.md",
]


def load_cache():
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache):
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def cache_key(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate_text(text, cache, translator):
    if not text.strip():
        return text
    key = cache_key(text)
    if key in cache:
        return cache[key]

    translated = translator.translate(text)
    translated = translated.replace("&quot;", '"').replace("&#39;", "'")
    cache[key] = translated
    if len(cache) % 25 == 0:
        save_cache(cache)
    return translated


def has_cjk(text):
    return bool(re.search(r"[\u3400-\u9fff]", text))


def github_slug(text):
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\s\u3400-\u9fff-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def translate_block(block, cache, translator):
    if not has_cjk(block):
        return block
    block = translate_link_labels(block, cache, translator)
    protected_pattern = r"(`[^`]+`|\[[^\]]+\]\([^)]+\)|\.\.?/[A-Za-z0-9_./#-]+)"
    parts = re.split(protected_pattern, block)
    translated_parts = []
    for part in parts:
        if not part:
            continue
        if re.fullmatch(protected_pattern, part) or not has_cjk(part):
            translated_parts.append(part)
        else:
            translated_parts.append(translate_text(part, cache, translator))
    return "".join(translated_parts)


def translate_link_labels(text, cache, translator):
    def replace(match):
        label, url = match.groups()
        if has_cjk(label):
            label = translate_text(label, cache, translator)
        return f"[{label}]({url})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, text)


def translate_table_line(line, cache, translator):
    if re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line):
        return line
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line
    leading_pipe = body.startswith("|")
    trailing_pipe = body.endswith("|")
    cells = body.strip("|").split("|")
    translated_cells = []
    for cell in cells:
        left = len(cell) - len(cell.lstrip(" "))
        right = len(cell) - len(cell.rstrip(" "))
        content = cell.strip()
        if content:
            content = translate_block(content, cache, translator)
        translated_cells.append(" " * left + content + " " * right)
    rendered = "|".join(translated_cells)
    if leading_pipe:
        rendered = "|" + rendered
    if trailing_pipe:
        rendered = rendered + "|"
    return rendered + newline


def translate_markdown_line(line, cache, translator):
    newline = "\n" if line.endswith("\n") else ""
    body = line[:-1] if newline else line

    if not body.strip() or not has_cjk(body):
        return line

    if body.startswith("|"):
        return translate_table_line(line, cache, translator)

    image_match = re.match(r"^(!\[)(.*?)(\]\(.+\))$", body)
    if image_match:
        return (
            image_match.group(1)
            + translate_block(image_match.group(2), cache, translator)
            + image_match.group(3)
            + newline
        )

    heading_match = re.match(r"^(#{1,6}\s+)(.+?)(\s*)$", body)
    if heading_match:
        return (
            heading_match.group(1)
            + translate_block(heading_match.group(2), cache, translator)
            + heading_match.group(3)
            + newline
        )

    quote_match = re.match(r"^(>\s*)(.+)$", body)
    if quote_match:
        return quote_match.group(1) + translate_block(quote_match.group(2), cache, translator) + newline

    list_match = re.match(r"^(\s*(?:[-*+]\s+|\d+\.\s+))(.*)$", body)
    if list_match:
        return list_match.group(1) + translate_block(list_match.group(2), cache, translator) + newline

    return translate_block(body, cache, translator) + newline


def translate_file(path, cache, translator):
    text = path.read_text(encoding="utf-8")
    out = []
    heading_map = {}
    paragraph = []
    in_code = False

    def flush_paragraph():
        if not paragraph:
            return
        joined = " ".join(line.strip() for line in paragraph)
        translated = translate_block(joined, cache, translator)
        out.append(translated + "\n")
        paragraph.clear()

    for line in text.splitlines(keepends=True):
        if line.startswith("```"):
            flush_paragraph()
            in_code = not in_code
            out.append(line)
            continue

        if in_code:
            out.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            out.append(line)
            continue

        special = (
            line.lstrip().startswith(("- ", "* ", "+ ", ">"))
            or re.match(r"^\s*\d+\.\s+", line)
            or line.startswith("#")
            or line.startswith("|")
            or line.startswith("![")
            or line.strip() == "---"
        )
        if special:
            flush_paragraph()
            translated = translate_markdown_line(line, cache, translator)
            out.append(translated)
            original_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            new_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", translated)
            if original_match and new_match:
                heading_map[github_slug(original_match.group(2))] = github_slug(new_match.group(2))
            continue

        paragraph.append(line)

    flush_paragraph()

    return "".join(out), heading_map


def rewrite_anchors(text, all_heading_maps):
    def replace(match):
        label, prefix, file_name, anchor = match.groups()
        prefix = prefix or ""
        map_name = file_name or "__self__"
        target_map = all_heading_maps.get(map_name, {})
        label_slug = github_slug(label)
        new_anchor = target_map.get(anchor, anchor)
        if new_anchor == anchor and label_slug in set(target_map.values()):
            new_anchor = label_slug
        return f"[{label}]({prefix}{file_name or ''}#{new_anchor})"

    return re.sub(r"\[([^\]]+)\]\((\.\/)?([^)#]+\.md)?#([^)]+)\)", replace, text)


def apply_manual_anchor_fixes(file_name, text):
    fixes = {
        "course-01-first-encounter.md": {
            "#第二章先建立任务直觉": "#chapter-ii-establishment-of-mission-intuition",
        },
        "course-04-tool-mechanism.md": {
            "#45-observation为下一轮决策提供依据": "#45-how-to-shape-the-next-round-of-decision-making",
            "[Next class connect.](#下一课衔接)": "Next class connect.",
        },
        "course-05-02-rag.md": {
            "#241-总览完整链路与本节路线图": "#241-overview-full-links",
        },
        "course-05-07-human-in-the-loop.md": {
            "[Summary of this chapter](#本章速记)": "Summary of this chapter",
        },
        "course-05-08-multi-agent.md": {
            "#83-reviewer-模式最简单的-multi-agent-入口": "#83-reviewer-mode-simple-multi-agent-mode",
        },
        "course-05-09-composition.md": {
            "[Cross-case comparison overview](#跨案例对比总览)": "Cross-case comparison overview",
        },
    }
    for old, new in fixes.get(file_name, {}).items():
        text = text.replace(old, new)
    return text


def main():
    TARGET_DIR.mkdir(exist_ok=True)
    cache = load_cache()
    translated_files = {}
    heading_maps = {}
    installed_languages = translate.get_installed_languages()
    from_lang = next(lang for lang in installed_languages if lang.code == "zh")
    to_lang = next(lang for lang in installed_languages if lang.code == "en")
    translator = from_lang.get_translation(to_lang)

    for file_name in FILES:
        print(f"Translating {file_name}...", flush=True)
        translated, heading_map = translate_file(SOURCE_DIR / file_name, cache, translator)
        translated_files[file_name] = translated
        heading_maps[file_name] = heading_map
        save_cache(cache)

    for file_name, translated in translated_files.items():
        maps = {"__self__": heading_maps[file_name], **heading_maps}
        final = rewrite_anchors(translated, maps)
        final = apply_manual_anchor_fixes(file_name, final)
        (TARGET_DIR / file_name).write_text(final, encoding="utf-8")

    save_cache(cache)
    print(f"Done. Wrote {len(FILES)} files to {TARGET_DIR}", flush=True)


if __name__ == "__main__":
    main()
