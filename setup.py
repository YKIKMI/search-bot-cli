from setuptools import setup, find_packages

setup(
    name="search-bot-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "openai",
        "pandas",
        "argparse",
        "aiofiles",
        "asyncio",
    ],
    entry_points={
        "console_scripts": [
            "search-bot=search_bot.search:main",
        ],
    },
    author="Yash Verma",
    description="AI-powered Google search automation tool.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YKIKMI/search-bot-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

