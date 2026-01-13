from setuptools import setup, find_packages

setup(
    name="ai-baby-generator",
    version="1767667.153.845",
    description="High-quality integration for https://supermaker.ai/image/ai-baby-generator/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/image/ai-baby-generator/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
