"""
Configuración de setuptools para iamex
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="iamex",
    version="0.0.6.pre1",
    author="Inteligencia Artificial México",
    author_email="hostmaster@iamex.io",
    description="Librería Python simple y poderosa para acceder a múltiples modelos de inteligencia artificial de forma unificada",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IA-Mexico/iamex",
    project_urls={
        "Bug Tracker": "https://github.com/IA-Mexico/iamex/issues",
        "Documentation": "https://github.com/IA-Mexico/iamex#readme",
        "Source Code": "https://github.com/IA-Mexico/iamex",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    keywords="ai, machine learning, inference, models, iamex, artificial intelligence, chat, conversational ai, llm, nlp, python, api client",
)
