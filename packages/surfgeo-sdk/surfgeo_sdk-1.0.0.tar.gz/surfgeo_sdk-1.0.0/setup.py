from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="surfgeo-sdk",
    version="1.0.0",
    author="surfgeo",
    author_email="support@surfgeo.com",
    description="Server-side AI bot tracking SDK for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thebisontech/surfgeo-python-aireferral-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/thebisontech/surfgeo-python-aireferral-sdk/issues",
        "Documentation": "https://github.com/thebisontech/surfgeo-python-aireferral-sdk/blob/main/docs/README.md",
    },
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Flask",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "httpx>=0.23.0",
    ],
    extras_require={
        "django": ["Django>=3.2"],
        "flask": ["Flask>=2.0"],
        "fastapi": ["fastapi>=0.95.0", "starlette>=0.26.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "django>=3.2",
            "flask>=2.0",
            "fastapi>=0.95.0",
        ],
    },
    keywords="surfgeo ai bot tracking analytics llm chatgpt perplexity claude middleware django flask fastapi",
)

