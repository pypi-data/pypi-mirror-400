from setuptools import setup, find_packages

setup(
    name="copyright-free-songs",
    version="1767774.444.65",
    description="High-quality integration for https://supermaker.ai/music/copyright-free-songs/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/music/copyright-free-songs/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
