from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nnmerge",
    version="0.1.2",
    author="Wawan Cenggoro",
    author_email="wawancenggoro@gmail.com",
    description="A library to merge multiple neural network models for parallel hyperparameter search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wawancenggoro/nnmerge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "torch>=1.9.0"
    ],
)

