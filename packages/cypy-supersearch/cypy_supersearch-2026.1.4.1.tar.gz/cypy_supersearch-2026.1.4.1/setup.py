from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cypy_supersearch",
    version="2026.1.4.1",
    description="A fast local file search tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Ke Yingjie",
    author_email="yingjieke@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "PySide6",
    ],
    entry_points={
        "console_scripts": [
            "supersearch=cypy_supersearch.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
)
