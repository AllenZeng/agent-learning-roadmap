# Agent Learning Roadmap

A systematic learning path for developers who want to understand, build, evaluate, and ship AI Agent systems.

[简体中文](README.zh-CN.md) | [English](README.md)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/AllenZeng/agent-learning-roadmap)
![Language](https://img.shields.io/badge/language-English%20%7C%20中文-blue.svg)

> Current status: v0.6. The Chinese course draft is available through course 08. The English version is available through course 05-09, with course 06-08 still in progress.

---

![Agent Learning Roadmap overview](assets/course-roadmap.svg)

---

## What Is This?

This project is a practical roadmap for learning how Agent products evolve from a minimal working loop into production-ready systems.

The central model is:

```text
Agent = Prompt + LLM Decision + Tool / Environment Interaction + State + Loop Control
```

RAG, Memory, Planning, Reflection, Multi-Agent, MCP, and Skills are important, but they are not mandatory modules for every Agent application. They should be introduced around the minimal Agent loop when a real scenario calls for them.

## Why This Project Exists

Many Agent learning resources jump directly into RAG, Tool Use, LangGraph, MCP, or Multi-Agent patterns. That often leaves learners with a common problem:

They know many terms, but they do not know what each capability solves, when to introduce it, or how to turn a demo into a reliable product system.

This project starts from a more grounded question:

> How does an Agent application evolve from a minimal loop into a system that is controllable, observable, recoverable, evaluable, and shippable?

The roadmap focuses on:

- the boundary between Chatbots, Workflows, and Agents;
- the minimal Agent loop and how it runs;
- when to introduce Tool Use, RAG, Memory, Planning, Reflection, and Multi-Agent patterns;
- how Agent Runtime / Harness architecture supports state, tools, context, evaluation, recovery, and governance;
- how Agent capabilities become real product experiences.

## Who It Is For

This project is for:

- developers who want a systematic path into AI Agent application development;
- learners who already know LLM APIs and want to go deeper into tools, RAG, memory, and runtime design;
- engineers moving from Agent demos to real products;
- product and technical leads who need to reason about Agent reliability, evaluation, safety, cost, and architecture.

It is not for:

- people who only want to copy a ready-made Agent template;
- people focused mainly on model training, fine-tuning, or low-level ML algorithms;
- readers who want a high-level concept tour without engineering practice.

## Quick Start

Start with the [syllabus](syllabus.md). It gives you the full map of the course, explains the learning layers, and helps you choose where to begin.

If you want a complete path, read the lessons in order. The course starts with product intuition, moves through Agent paradigm evolution, then builds up the minimal loop, tool mechanism, scenario enhancements, runtime architecture, and productization.

If you already have a specific goal, use the course table below. For example, start with lesson 03 if you want to build a minimal Agent, lesson 04 if you want to understand tool calling, and lesson 05 if you want to decide when to introduce RAG, Memory, Planning, Reflection, or Multi-Agent patterns.

## Course Structure

| Lesson | Time | Focus | English |
| --- | --- | --- | --- |
| [01. First Encounter with Agents](courses-en/course-01-first-encounter.md) | 0.5-1 day | Build product intuition and an observation framework | Available |
| [02. Agent Paradigm Evolution](courses-en/course-02-evolution.md) | 1-2 days | Understand why the Agent paradigm emerged | Available |
| [03. Minimal Agent Loop](courses-en/course-03-minimal-agent-loop.md) | 2-4 days | Build the smallest runnable Agent loop | Available |
| [04. Tool Mechanism](courses-en/course-04-tool-mechanism.md) | 2-4 days | Turn tool calling into a controllable mechanism | Available |
| [05. Scenario Enhancement Capabilities](courses-en/course-05-01-scenario-enhancement.md) | 2-5 days | Decide when extra capabilities are worth adding | Available |
| [06. Harness Runtime Architecture](courses/course-06-runtime-architecture.md) | 4-7 days | Engineer the minimal loop into a runtime harness | Chinese only |
| [07. Agent Productization](courses/course-07-productization.md) | 2-4 days | Design trust, recovery, safety, metrics, and cost controls | Chinese only |
| [08. Project Practice and Ecosystem Tracking](courses/course-08-project-practice.md) | 5-10 days | Build an integrated Agent project | Chinese only |

Complete study usually takes 3-6 weeks. Reading the roadmap is much faster; building and validating the exercises takes more time.

## Examples

The repository includes runnable examples:

- `examples/course-03-minimal-agent`: minimal Agent loop;
- `examples/course-04-tool-mechanism`: tool mechanism;
- `examples/course-05-02-rag`: RAG / external knowledge access;
- `examples/course-05-03-memory`: memory / state continuity;
- `examples/course-05-04-context-engineering`: context engineering;
- `examples/course-05-05-planning`: planning / workflow patterns;
- `examples/course-05-06-reflection`: reflection / feedback loop;
- `examples/course-05-07-human-in-the-loop`: human-in-the-loop;
- `examples/course-05-08-multi-agent`: multi-agent collaboration.

## Repository Layout

```text
README.md              # English project entry
README.zh-CN.md        # Simplified Chinese project entry
syllabus.md            # English syllabus
syllabus.zh-CN.md      # Simplified Chinese syllabus
courses/               # Chinese course content
courses-en/            # English course content
assets/                # Shared diagrams and visual assets
examples/              # Shared runnable examples
reference/             # Supplementary references
```

The default GitHub entry is English. Chinese readers can use the full [Simplified Chinese README](README.zh-CN.md).

## Contributing

Contributions are welcome:

- content fixes: typos, broken links, concept clarification;
- content additions: new sections, deeper examples, or improved explanations;
- translation: English or other language versions;
- code examples: new or improved examples for each lesson.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project uses a dual-license model:

- documentation, course content, diagrams, and explanatory text: [CC BY-SA 4.0](LICENSE);
- example code, demos, and scripts: [MIT](LICENSE-CODE), unless a specific directory states otherwise.

You may copy, distribute, and adapt the course content, including for commercial use, as long as attribution is preserved and derivative documentation is shared under the same license.
