from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ncbi-mcp",
    version="0.1.1",
    author="goki",
    author_email="654051206@qq.com",
    description="NCBI E-utilities MCP server for accessing NCBI databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goki/ncbi-mcp",
    packages=find_packages(where="scr"),
    package_dir={"": "scr"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ncbi-mcp=ncbi_mcp.server:main",
        ],
    },
)