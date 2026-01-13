from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="logita",
    version="1.3.0",  # Actualicé la versión a 1.2.1
    author="Jose Luis Coyotzi",
    author_email="jlci811122@gmail.com",
    description="A simple and colorful logging utility for console output with support for context manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,  # Incluye archivos estáticos como README, LICENSE
    install_requires=[
        "colorama>=0.4.6",  # Especifica versión mínima
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",  # Tu paquete tiene type hints
    ],
    python_requires='>=3.6'
)
