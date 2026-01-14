from setuptools import setup, find_packages

setup(
    name="py-lostark",
    version="0.1.0",
    description="Python wrapper library for LostArk API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Author Name",
    author_email="author@example.com",
    url="https://github.com/DAN-MU-ZI/pyLoa",
    packages=find_packages(include=["pyloa", "pyloa.*"]),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
