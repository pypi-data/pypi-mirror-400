# Ibraahim

**A Minimalist, Provider-Agnostic LLM Framework**

Ibraahim is a lightweight Python library designed to bring sanity and stability to LLM application development. It solves the "provider lock-in" problem by giving you a single, unified interface to interact with any Large Language Model (OpenAI, Anthropic, etc.).

## 🚀 The Core Value Proposition

In a world of complex, "magical" AI agents and opaque frameworks, **Ibraahim** stands for clarity and control.

*   **🚫 No Hidden Magic**: No autonomous agents running in loops you can't see. No "black box" logic.
*   **🔌 Provider Agnostic**: Switch from GPT-4 to Claude 3.5 Sonnet with a single line of config. Your business logic stays exactly the same.
*   **🛡️ Deterministic by Design**: "Data In, Data Out". Every interaction is explicit, debuggable, and predictable.

## 🎯 The End Result

When you use Ibraahim, you get:

1.  **Stable Codebase**: Your application code doesn't break just because an API provider changed their SDK.
2.  **Clean Architecture**: Separation of concerns between *what* you want to say (Prompts) and *who* says it (Providers).
3.  **Freedom of Choice**: You are never locked into one AI vendor.

## 🛠️ How It Works

Ibraahim provides three simple, powerful building blocks:

1.  **Prompts**: Reusable templates for your inputs.
2.  **LLMs**: Unified wrappers for API providers.
3.  **Chains**: Simple links that connect a Prompt to an LLM to produce a Result.

---
*Build with confidence. Build with Ibraahim.*
