from setuptools import setup, find_packages

setup(
    name="ai-soulmate-sketch-filter",
    version="1767855.550.683",
    description="High-quality integration for https://supermaker.ai/image/blog/ai-soulmate-drawing-free-tool-generate-your-soulmate-sketch/",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="SuperMaker",
    url="https://supermaker.ai/image/blog/ai-soulmate-drawing-free-tool-generate-your-soulmate-sketch/",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
