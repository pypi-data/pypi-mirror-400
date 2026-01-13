"""
LatencyZero Python SDK Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="latencyzero",
    version="0.1.1",
    author="LatencyZero Team",
    author_email="hello@latencyzero.ai",
    description="Cut API latency by 50-90% with Adaptive Anticipatory Approximation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/latencyzero/latencyzero",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
)
