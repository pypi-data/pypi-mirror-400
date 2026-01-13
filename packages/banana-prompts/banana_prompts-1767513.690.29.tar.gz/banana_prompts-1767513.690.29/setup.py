from setuptools import setup, find_packages

setup(
    name="banana-prompts",
    version="1767513.690.29",
    description="High-quality integration for https://bananaproai.com/banana-prompts/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://bananaproai.com/banana-prompts/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
