from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paizhaojieti-stdio-mcp",
    version="1.0.0",
    author="Yutian",
    author_email="your.email@example.com",
    description="基于智谱AI拍照解题智能体的STDIO类型MCP服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/La0bALanG/paizhaojieti_stdio_mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "paizhaojieti-mcp=paizhaojieti_stdio_mcp_package.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "paizhaojieti_stdio_mcp_package": ["*.json", "*.md", "*.txt"],
    },
)