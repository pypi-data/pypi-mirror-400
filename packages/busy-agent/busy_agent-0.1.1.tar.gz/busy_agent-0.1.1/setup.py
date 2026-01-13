#!/usr/bin/env python3
"""
Setup configuration for Busy Agent package
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open('README_FULL.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='busy-agent',
    version='0.1.1',
    author='Busy Agent Contributors',
    author_email='',
    description='模拟 ReAct Agent 工作过程 - Simulate ReAct Agent working process',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/demouo/busy-agent',
    packages=find_packages(),
    package_data={
        'busy_agent': [
            'data/config.json',
            'data/datasets/*.parquet',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'busy-agent=busy_agent.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    keywords='agent react llm simulation',
    project_urls={
        'Bug Reports': 'https://github.com/demouo/busy-agent/issues',
        'Source': 'https://github.com/demouo/busy-agent',
    },
)
