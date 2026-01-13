from setuptools import setup, find_packages


setup(
    name="savekit",
    version="2.0.1",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy>=2.0.0",
        "pydantic>=1.10.0"
    ],
    description="A lightweight, persistent key-value storage toolkit for Python projects, using SQLite via SQLAlchemy. Supports primitive types, complex objects, and Pydantic models with context manager support and project-root storage.",
    author="Jose Luis Coyotzi",
    author_email="jlci811122@gmail.com",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
