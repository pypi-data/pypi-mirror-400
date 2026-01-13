# PromptFletcher 🚀
### Deterministic Auto-Prompt Engineering for Python & NLP

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/promptfletcher)
![PyPI - License](https://img.shields.io/pypi/l/promptfletcher)
![PyPI](https://img.shields.io/pypi/v/promptfletcher)
![PyPI - Status](https://img.shields.io/pypi/status/promptfletcher)
![PyPI - Monthly Downloads](https://img.shields.io/pypi/dm/promptfletcher)
![Total Downloads](https://static.pepy.tech/badge/promptfletcher)

---

## Overview

PromptFletcher is a lightweight, deterministic, and dependency-minimal Python library for automatic prompt refinement using classical NLP heuristics.

Unlike LLM-based prompt optimizers, PromptFletcher:

- Does not require external APIs
- Does not use large transformer models
- Works offline
- Produces reproducible results
- Is fast enough for CI, batch jobs, and research pipelines

It is ideal for developers, researchers, and teams who want structured prompt improvement without LLM overhead.

---

## Key Capabilities

- Heuristic-based prompt evaluation
- Iterative prompt refinement
- Context-aware relevance scoring
- Fast execution using NLTK
- Deterministic and reproducible behavior
- Minimal runtime footprint

---

## Installation

### Install from PyPI (recommended)

pip install promptfletcher

### Install from GitHub (latest)

pip install git+https://github.com/Vikhram-S/PromptFletcher.git

On first use, required NLTK resources are downloaded automatically.

---

## Quick Start

### Initialize the Engine

from promptfletcher import AutoPromptEngineer

engineer = AutoPromptEngineer()

### Define Context and Prompt

context = "We are optimizing prompt quality for large language models."
prompt = "How improve AI responses"

### Refine the Prompt

refined = engineer.refine_prompt(prompt, context)
print(refined)

Example output:

How improve AI responses? Please explain in detail.

---

## How It Works

PromptFletcher applies classical NLP heuristics to evaluate and refine prompts:

| Heuristic  | Description |
|-----------|-------------|
| Length    | Penalizes prompts that are too short or too verbose |
| Clarity   | Rewards explicit questions |
| Relevance | Measures keyword overlap with context |
| Iteration | Keeps only prompt improvements |

This design makes the system predictable, explainable, and easy to debug.

---

## API Reference

### AutoPromptEngineer

refine_prompt(prompt: str, context: str, iterations: int = 3) -> str  
Refines a prompt iteratively using heuristic scoring.

evaluate_prompt(prompt: str, context: str) -> float  
Returns a numeric quality score for a prompt.

---

## Use Cases

- Prompt standardization in teams
- Automated prompt cleanup pipelines
- Prompt benchmarking
- Research experiments
- CI validation of prompts
- Offline prompt tuning
- Educational NLP projects

---

## Dependencies

PromptFletcher keeps dependencies intentionally minimal:

- nltk >= 3.6
- numpy >= 1.21
- regex >= 2023.3.23

---

## License

PromptFletcher is released under the MIT License.  
You are free to use, modify, and distribute this software.

---

## Contributing

Contributions are welcome.

Workflow:

1. Fork the repository
2. Create a branch (feature/your-feature)
3. Commit your changes
4. Push and open a Pull Request

Please ensure code is typed, documented, and non-breaking.

---

## Support and Contact

Issues: https://github.com/Vikhram-S/PromptFletcher/issues  
Email: vikhrams@saveetha.ac.in

---

## Support the Project

If PromptFletcher helps you:

- Star the repository
- Use it in your projects
- Share it with others

Your support helps grow the project.
