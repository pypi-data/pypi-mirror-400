from setuptools import setup, find_packages

setup(
    name="makeshot.ai",
    version="1767497.11.800",
    description="High-quality integration for https://makeshot.ai/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://makeshot.ai/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
