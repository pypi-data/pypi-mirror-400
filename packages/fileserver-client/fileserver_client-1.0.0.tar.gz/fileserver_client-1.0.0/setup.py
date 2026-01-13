from setuptools import setup, find_packages

setup(
    name="fileserver-client",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="FileServer Team",
    description="Python client for FileServer API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fileserver",
    keywords="fileserver, api, client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
