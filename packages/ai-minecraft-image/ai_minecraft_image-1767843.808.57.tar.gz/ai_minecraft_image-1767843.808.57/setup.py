from setuptools import setup, find_packages

setup(
    name="ai-minecraft-image",
    version="1767843.808.57",
    description="High-quality integration for https://supermaker.ai/image/blog/how-to-turn-your-image-into-minecraft-skin/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/image/blog/how-to-turn-your-image-into-minecraft-skin/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
