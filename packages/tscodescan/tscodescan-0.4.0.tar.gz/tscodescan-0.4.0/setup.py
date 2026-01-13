from setuptools import setup, find_packages

setup(
    name="tscodescan",
    version="0.4.0",
    description="repository artifact generator",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tscodescan=scan.cli:main",
            "tsc=scan.cli:main",
        ]
    },
    python_requires=">=3.8",
)
