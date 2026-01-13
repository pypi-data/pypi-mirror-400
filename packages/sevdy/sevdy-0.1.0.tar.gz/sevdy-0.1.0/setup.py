from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sevdy",
    version="0.1.0",
    author="Sevdiyorov",
    author_email="sevdiorov@gmail.com",
    description="Sevdy - Your personal Python code cleaner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sevdiyorov/sevdy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sevdy=sevdy.cli:main",
        ],
    },
)