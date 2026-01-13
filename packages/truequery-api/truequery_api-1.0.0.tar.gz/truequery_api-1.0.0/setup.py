from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="truequery-api",
    version="1.0.0",
    author="Leo",
    author_email="leoofficial@gmail.com",
    description="Python client for TrueQuery API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    py_modules=["truequery"],  # Важно: указываем один файл
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "truequery=truequery:_cli_main",
        ],
    },
)