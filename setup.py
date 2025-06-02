#!/usr/bin/env python3
"""
楓之谷風格角色行走圖製作工具安裝腳本
"""

from setuptools import setup, find_packages
import os

# 讀取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 讀取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="maplestory-sprite-generator",
    version="1.0.0",
    description="楓之谷風格角色行走圖AI生成工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AI Assistant",
    author_email="assistant@example.com",
    url="https://github.com/yourusername/maplestory-sprite-generator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Artistic Software",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ai, sprite, animation, pixel-art, maplestory, stable-diffusion",
    entry_points={
        "console_scripts": [
            "ms-sprite-gen=main:main",
            "ms-web-ui=web_ui:main",
        ],
    },
    package_data={
        "": ["configs/*.yaml", "*.md", "*.txt"],
    },
    zip_safe=False,
) 