from setuptools import setup, find_packages

setup(
    name="minedb",
    version="1.0.1",
    author="Harsh Singh Sikarwar",
    description="A lightweight encrypted local database using dictionary-based storage",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/harshsikarwar/MineDB",
    project_urls={
        "Source": "https://github.com/harshsikarwar/MineDB",
        "Issues": "https://github.com/harshsikarwar/MineDB/issues",
    },
    license="MIT",
    python_requires=">=3.9",
    install_requires=[
        "cryptography>=41.0.0"
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
