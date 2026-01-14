from setuptools import setup, find_packages

setup(
    name="langchian",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["pyperclip"],
    description="Toy library that copies LangChain RAG code to clipboard",
    author="",
)
