from setuptools import setup, find_packages

setup(
    name="first-last-frame",
    version="1767774.631.530",
    description="High-quality integration for https://supermaker.ai/video/first-last-frame/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/video/first-last-frame/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
