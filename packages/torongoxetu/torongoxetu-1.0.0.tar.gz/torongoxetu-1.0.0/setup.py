from setuptools import setup, find_packages
import os

setup(
    name="torongoxetu",
    version="1.0.0",
    description="A inference library for the TorongoXetu Assamese ASR model.",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="Anand Dey",
    author_email="ananddey.nic@gmail.com",
 
    packages=find_packages(),
    install_requires=[
        "torch",
        "numpy",
        "soundfile",
        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
