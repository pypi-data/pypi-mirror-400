from setuptools import setup, find_packages

setup(
    name="coleslaw_api",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.5",
        "aiomysql>=0.1.1",
    ],
    python_requires=">=3.10",
    url="https://github.com/DiscoKnax6808/Coleslaw",
    author="Exception2018",
    author_email="knax6808real22@gmail.com",
    description="Fast Python web server with async MySQL and routing",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
)
