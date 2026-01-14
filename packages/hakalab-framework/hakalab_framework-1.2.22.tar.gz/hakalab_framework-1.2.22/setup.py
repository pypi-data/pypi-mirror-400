#!/usr/bin/env python3
"""
Setup configuration for playwright-behave-framework
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="hakalab-framework",
    version="1.1.21",
    author="Felipe Farias",  # 👈 CAMBIAR: Tu nombre real
    author_email="felipe.farias@hakalab.com",  # 👈 CAMBIAR: Tu email
    description="Framework completo de pruebas funcionales con Playwright y Behave",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pipefariashaka/hakalab-framework.git",  # 👈 CAMBIAR: Tu repositorio
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "allure": [
            "allure-commandline>=2.20.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "haka-init=hakalab_framework.cli:init_project",
            "haka-run=hakalab_framework.cli:run_tests",
            "haka-report=hakalab_framework.cli:generate_report",
            "haka-steps=hakalab_framework.cli:list_steps",
            "haka-validate=hakalab_framework.cli:validate_project",
            "haka-html=hakalab_framework.cli_html_report:html_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "hakalab_framework": [
            "templates/*.feature",
            "templates/*.json",
            "templates/*.py",
            "templates/*.ini",
            "templates/*.env",
            "templates/*.md",
        ],
    },
    keywords="playwright behave bdd testing automation functional-testing",
    project_urls={
        "Bug Reports": "https://github.com/[TU-USUARIO]/playwright-behave-framework/issues",  # 👈 CAMBIAR
        "Source": "https://github.com/[TU-USUARIO]/playwright-behave-framework",  # 👈 CAMBIAR
        "Documentation": "https://github.com/[TU-USUARIO]/playwright-behave-framework#readme",  # 👈 CAMBIAR
    },
)