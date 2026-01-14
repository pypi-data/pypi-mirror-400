from setuptools import setup, find_packages

setup(
    name="aipresenter",
    version="0.1.0",
    description="A library to format AI responses with Markdown, syntax highlighting, and copy buttons.",
    packages=find_packages(),
    install_requires=[
        "markdown-it-py",
        "Pygments"
    ],
)