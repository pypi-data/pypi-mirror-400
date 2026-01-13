from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-shell",
    version="1.2.0",
    author="wjr-2015",
    author_email="wangjinrui_150328@126.com",
    description="A GitHub simulation shell with automatic update feature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wjr-2015/github-shell",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.25.0",
        "cryptography>=38.0.0",
    ],
    entry_points={
        'console_scripts': [
            'github-shell=github_shell.main:main',
        ],
    },
)
