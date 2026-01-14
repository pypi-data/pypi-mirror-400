# myproject/setup.py

from setuptools import setup, find_packages

setup(
    name="endee",
    version="0.1.b6",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        "requests>=2.28.0",
        "httpx[http2]>=0.28.1",
        "numpy>=2.2.4",
        "msgpack>=1.1.0",
        "cryptography>=41.0.0",
    ],
    author="Endee Labs",
    author_email="dev@endee.io",
    description="Endee is the Next-Generation Vector Database for Scalable, High-Performance AI",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://endee.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)