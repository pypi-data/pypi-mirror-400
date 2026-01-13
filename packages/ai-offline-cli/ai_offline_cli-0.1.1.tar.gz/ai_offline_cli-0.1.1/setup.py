"""Setup script for AI CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-offline-cli",
    version="0.1.1",
    author="AI CLI Team",
    description="Offline AI assistant for code writing, command execution, and chat working with any offline models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "llama-cpp": ["llama-cpp-python"],
        "gpu": ["pynvml"],
        "all": ["llama-cpp-python", "pynvml"],
    },
    entry_points={
        "console_scripts": [
            "ai-cli=ai_cli.cli:main",
        ],
    },
)
