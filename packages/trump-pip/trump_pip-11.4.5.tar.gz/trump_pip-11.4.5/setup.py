from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trump-pip",
    version="11.4.5",
    description="A pip-like tool with Trump policy simulations and multi-language support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ruin321 and schooltaregf",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/trump-pip",
    packages=find_packages(include=['trump_pip', 'export_license']),
    entry_points={
        "console_scripts": [
            "tpip=trump_pip.cli:main",
            "tel=trump_pip.tel:main",
        ],
    },
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    keywords="pip, package manager, tpip, trump, simulation, export license",
)
