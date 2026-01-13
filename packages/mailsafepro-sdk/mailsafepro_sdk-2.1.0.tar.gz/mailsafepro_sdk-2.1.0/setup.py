"""
Setup script for MailSafePro SDK
Fallback for environments that don't support pyproject.toml
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mailsafepro-sdk",
    version="2.1.0",
    author="MailSafePro Team",
    author_email="support@mailsafepro.com",
    description="Official Python SDK for MailSafePro Email Validation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mailsafepro/mailsafepro-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/mailsafepro/mailsafepro-python-sdk/issues",
        "Documentation": "https://docs.mailsafepro.com/sdk/python",
        "Source Code": "https://github.com/mailsafepro/mailsafepro-python-sdk",
        "Changelog": "https://github.com/mailsafepro/mailsafepro-python-sdk/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    package_data={
        "mailsafepro": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
        "Topic :: Security",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0,<1.0.0",
        "pydantic>=2.0.0,<3.0.0",
    ],
    extras_require={
        "async": [
            "aiofiles>=23.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.1",
            "pytest-asyncio>=0.21.0",
            "respx>=0.20.0",
            "black>=24.3.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
            "bandit>=1.7.5",
            "safety>=3.0.0",
        ],
    },
)
