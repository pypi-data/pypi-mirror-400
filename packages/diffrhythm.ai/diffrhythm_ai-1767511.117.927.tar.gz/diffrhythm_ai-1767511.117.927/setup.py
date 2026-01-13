from setuptools import setup, find_packages

setup(
    name="diffrhythm.ai",
    version="1767511.117.927",
    description="High-quality integration for https://diffrhythm.ai/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://diffrhythm.ai/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
