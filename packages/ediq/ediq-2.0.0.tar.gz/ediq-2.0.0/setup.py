from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ediq",
    version="2.0.0",
    author="Wyzcon",
    author_email="jonathan.cruz@wyzcon.com",
    description="Official Python SDK for Ediq AI Detection API - Education & HR modes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wyzcon/ediq-python",
    project_urls={
        "Bug Tracker": "https://github.com/wyzcon/ediq-python/issues",
        "Documentation": "https://docs.wyzcon.com",
        "Homepage": "https://wyzcon.com",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    py_modules=["ediq"],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    keywords="ai detection artificial intelligence plagiarism checker education hr resume cover letter linkedin wyzcon ediq",
)
