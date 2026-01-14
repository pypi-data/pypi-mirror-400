#  Copyright (c) 2026 CUJO LLC
from pathlib import Path

import setuptools

with Path("README.md").open() as fh:
    long_description = fh.read()

setuptools.setup(
    name="test-step",
    version="1.0.0",
    author="CUJO AI TestOps",
    author_email="testops@cujo.com",
    description="Test step decorator and HTML reporting plugin for pytest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cujoai/test-step",
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        "pytest11": [
            "ctr_html_reporting = test_step.html_reporting.plugin",
            "ctr_steps = test_step.steps.plugin",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: Pytest"
    ],
    python_requires='>=3.10',
    install_requires=[
        'pytest>=8,<10',
        'pytest-xdist~=3.8',
        'pytest-html~=4.1'
    ],
    extras_require={
        'test': [
            'junitparser~=4.0',
            'ruff==0.12',
        ]
    }
)
