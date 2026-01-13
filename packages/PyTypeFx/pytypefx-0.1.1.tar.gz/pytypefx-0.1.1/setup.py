from setuptools import find_packages, setup

setup(
    name="PyTypeFx",
    version="0.1.1",
    author="RK RIAD KHAN",
    author_email="rkriad585@gmail.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    url="https://github.com/rkstudio585/TypeFx",
    description="A Python library for creating captivating terminal typing effects with ease.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",    
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={"console_scripts": ["typefx = TypeFx.cli:main"]},
)
