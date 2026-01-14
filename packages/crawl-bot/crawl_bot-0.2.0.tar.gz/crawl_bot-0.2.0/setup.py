"""Setup module."""

from typing import List

from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


def read_requirements(path: str = 'requirements.txt') -> List[str]:
    """Return cleaned requirement lines from a requirements file."""
    with open(path, 'r', encoding='utf-8') as requirements:
        return [
            line.strip()
            for line in requirements
            if line.strip() and not line.startswith('#')
        ]


setup(
    name='crawl-bot',
    version='0.2.0',
    packages=find_packages(),
    install_requires=read_requirements(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
