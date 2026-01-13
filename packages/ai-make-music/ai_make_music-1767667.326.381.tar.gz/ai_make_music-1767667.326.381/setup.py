from setuptools import setup, find_packages

setup(
    name="ai-make-music",
    version="1767667.326.381",
    description="High-quality integration for https://supermaker.ai/music/ai-make-music/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/music/ai-make-music/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
