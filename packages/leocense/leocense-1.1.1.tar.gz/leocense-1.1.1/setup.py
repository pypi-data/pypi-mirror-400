from setuptools import setup, find_packages

setup(
    name="leocense",
    version="1.1.1",
    description="Official Python SDK for LEOCENSE",
    author="LEOCENSE",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
