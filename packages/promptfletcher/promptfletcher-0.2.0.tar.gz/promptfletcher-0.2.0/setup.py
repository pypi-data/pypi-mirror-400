from setuptools import setup, find_packages
from pathlib import Path

# ------------------------------------------------------------------
# Package metadata
# ------------------------------------------------------------------

PACKAGE_NAME = "promptfletcher"
VERSION = "0.2.0"

ROOT_DIR = Path(__file__).parent
README = (ROOT_DIR / "README.md").read_text(encoding="utf-8")

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Vikhram S",
    author_email="vikhrams@saveetha.ac.in", 
    license="MIT",
    description=(
        "PromptFletcher is a lightweight, deterministic auto-prompt "
        "engineering library for NLP and LLM workflows."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Vikhram-S/PromptFletcher",

    # 🔍 Keywords strongly affect PyPI search ranking
    keywords=[
        "prompt-engineering",
        "llm",
        "nlp",
        "natural-language-processing",
        "ai",
        "machine-learning",
        "prompt-optimization",
        "chatgpt",
        "generative-ai",
    ],

    packages=find_packages(exclude=("tests", "examples", "docs")),
    include_package_data=True,

    install_requires=[
        "nltk>=3.6",
        "numpy>=1.21",
        "regex>=2023.3.23",
    ],

    python_requires=">=3.7,<3.14",

    classifiers=[
        # Status & audience
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",

        # License
        "License :: OSI Approved :: MIT License",

        # Python versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Topics (VERY important for reach)
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],

    project_urls={
        "Homepage": "https://github.com/Vikhram-S/PromptFletcher",
        "Documentation": "https://github.com/Vikhram-S/PromptFletcher#readme",
        "Source": "https://github.com/Vikhram-S/PromptFletcher",
        "Bug Tracker": "https://github.com/Vikhram-S/PromptFletcher/issues",
        "Changelog": "https://github.com/Vikhram-S/PromptFletcher/releases",
    },
)
