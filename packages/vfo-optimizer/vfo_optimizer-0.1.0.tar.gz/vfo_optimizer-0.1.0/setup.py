from setuptools import setup, find_packages

setup(
    name="vfo-optimizer",
    version="0.1.0",
    description="Van Fish Optimization (VFO) Algorithm",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md").read() else "",
    long_description_content_type="text/markdown",
    author="Emine AYAZ Ph.D.",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
