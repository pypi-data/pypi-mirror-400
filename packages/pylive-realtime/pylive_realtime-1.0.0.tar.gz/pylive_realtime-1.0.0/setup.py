#!/usr/bin/env python3
"""Setup script for PyLive."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pylive-realtime",
    version="1.0.0",
    author="nano3",
    author_email="",
    description="PyLive: Python Realtime Streaming Platform with WebSocket, SSE, Chat, DM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Web3-League/pylive",
    project_urls={
        "Documentation": "https://github.com/Web3-League/pylive#readme",
        "Bug Reports": "https://github.com/Web3-League/pylive/issues",
        "Source": "https://github.com/Web3-League/pylive",
    },
    packages=find_packages(),
    package_data={
        "pylive": ["ui/*.py"],
    },
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "websockets>=11.0",
        "pyjwt>=2.8.0",
        "pydantic>=2.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "ui": [
            "streamlit>=1.28.0",
            "streamlit-shadcn-ui>=0.1.0",
            "requests>=2.31.0",
            "websocket-client>=1.6.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pylive=pylive.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="realtime websocket sse chat streaming fastapi",
    license="MIT",
)
