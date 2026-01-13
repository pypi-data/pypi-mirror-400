from setuptools import setup, find_packages

setup(
    name="baihu-logging",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="Baihu",
    author_email="baihu3210@gmail.com",
    description="A logging bot which can log messages to Discord",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/baihufox3210/Baihu-Logging",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)