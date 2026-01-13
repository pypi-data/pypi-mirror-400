from setuptools import setup, find_packages

setup(
    name="aiforge-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "aiforge=cli:main",
        ],
    },
)
