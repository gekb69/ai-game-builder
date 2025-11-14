"""
Setup script for AutoFlowAI
"""
from setuptools import setup, find_packages
from pathlib import Path

# قراءة README
this_directory = Path(__file__).parent
long_description = (this_directory / "docs/README.md").read_text(encoding='utf-8')

setup(
    name="autoflowai",
    version="2.0.0",
    author="AutoFlowAI Team",
    author_email="team@autoflowai.com",
    description="نظام ذكي متقدم لإدارة العمليات والمهام",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/autoflowai/autoflowai",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.9.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "asyncio",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.9.0",
            "isort>=5.9.0",
            "flake8>=4.0.0",
        ],
        "web": [
            "fastapi>=0.70.0",
            "uvicorn>=0.15.0",
            "jinja2>=3.0.0",
        ],
        "ml": [
            "tensorflow>=2.6.0",
            "torch>=1.9.0",
            "transformers>=4.12.0",
        ],
        "database": [
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
            "pymongo>=3.12.0",
        ],
        "security": [
            "cryptography>=3.4.0",
            "python-jose>=3.3.0",
            "passlib>=1.7.0",
        ],
        "monitoring": [
            "structlog>=21.1.0",
            "sentry-sdk>=1.3.0",
        ],
        "all": [
            "fastapi>=0.70.0",
            "uvicorn>=0.15.0",
            "jinja2>=3.0.0",
            "tensorflow>=2.6.0",
            "sqlalchemy>=1.4.0",
            "psycopg2-binary>=2.9.0",
            "pymongo>=3.12.0",
            "cryptography>=3.4.0",
            "python-jose>=3.3.0",
            "passlib>=1.7.0",
            "structlog>=21.1.0",
            "sentry-sdk>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "autoflowai=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "autoflowai": [
            "web/static/*",
            "web/static/css/*",
            "web/static/js/*",
            "web/templates/*",
            "docs/*",
        ],
    },
    zip_safe=False,
    keywords="ai automation workflow agent reasoning trading portfolio management",
    project_urls={
        "Bug Reports": "https://github.com/autoflowai/autoflowai/issues",
        "Source": "https://github.com/autoflowai/autoflowai",
        "Documentation": "https://autoflowai.readthedocs.io",
    },
)
