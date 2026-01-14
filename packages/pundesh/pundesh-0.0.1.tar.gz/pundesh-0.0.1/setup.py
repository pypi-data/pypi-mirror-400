from setuptools import setup, find_packages

setup(
    name="pundesh",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "pandas>=1.5.0",
    ],
    extras_require={
        "stealth": ["playwright-stealth>=1.0.6"],
    },
    python_requires=">=3.8",
)
