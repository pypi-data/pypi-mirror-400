from setuptools import setup, find_packages

setup(
    name="sora-ai-video",
    version="1767580.963.83",
    description="High-quality integration for https://supermaker.ai/video/sora-ai-video/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/video/sora-ai-video/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
