
from setuptools import setup, find_packages

setup(
    name="unstdlibpy",
    version="0.1.0.0.2",
    packages=find_packages(),
    author="Chen Yuxuan",
    author_email="null_3@qq.com",
    description="A ligntweight package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)


