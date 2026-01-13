"""
RevHold Python SDK setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="revhold-python",
    version="1.0.0",
    description="Official Python SDK for RevHold - AI business assistant for SaaS analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RevHold",
    author_email="support@revhold.io",
    url="https://www.revhold.io",
    project_urls={
        "Documentation": "https://www.revhold.io/docs",
        "Source": "https://github.com/revhold/python-sdk",
        "Tracker": "https://github.com/revhold/python-sdk/issues",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "mypy>=0.990",
            "types-requests>=2.28.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords=[
        "revhold",
        "analytics",
        "saas",
        "ai",
        "usage-tracking",
        "churn-analysis",
        "business-intelligence",
    ],
    license="MIT",
    zip_safe=False,
)

