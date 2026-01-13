from setuptools import setup, find_packages

setup(
    name="gengar",  # CHANGE 'yourname' to make it unique
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple library for AI/ML algorithm code snippets",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)