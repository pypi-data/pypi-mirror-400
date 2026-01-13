from setuptools import setup, find_packages

setup(
    name="sm-chat",
    version="1767581.686.835",
    description="High-quality integration for https://supermaker.ai/chat/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/chat/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
