from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="v5-relevance",
    version="1.1.4",
    author="元龙居士",
    author_email="your-email@example.com",
    description="V5版相关度算法 - 基于jieba的中文文本相关度计算",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/v5-relevance",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "jieba>=0.42.1",
    ],
    extras_require={
        "full": [
            "jieba>=0.42.1",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
    entry_points={
        "console_scripts": [
            "v5-relevance=v5:main",
        ],
    },
)
